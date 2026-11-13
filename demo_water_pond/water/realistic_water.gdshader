// 写实水面着色器（Godot 4.x）
// 特性：解析波浪法线、双层程序涟漪法线、深度感知屏幕折射、Beer-Lambert 水体吸收、
//       菲涅尔 + 环境反射、岸边/浪尖泡沫。
// 全部参数以 uniform 暴露，可在 Inspector 或 demo 内置面板里实时调节。
shader_type spatial;
render_mode blend_mix, depth_draw_opaque, cull_disabled, diffuse_burley, specular_schlick_ggx;

uniform sampler2D screen_tex : hint_screen_texture, filter_linear_mipmap;
uniform sampler2D depth_tex : hint_depth_texture, filter_linear_mipmap, repeat_disable;

// ---------------- 水体
uniform vec4 shallow_color : source_color = vec4(0.36, 0.62, 0.60, 1.0);
uniform vec4 deep_color : source_color = vec4(0.03, 0.16, 0.22, 1.0);
uniform float clarity : hint_range(0.1, 8.0) = 0.60;

// ---------------- 大浪（顶点位移，解析法线）
uniform float wave_height : hint_range(0.0, 0.35) = 0.055;
uniform float wave_scale : hint_range(0.02, 0.6) = 0.22;
uniform float wave_speed : hint_range(0.0, 3.0) = 0.6;
uniform float wave_chop : hint_range(0.0, 1.0) = 0.35;

// ---------------- 细节涟漪（片元法线）
uniform float ripple_scale : hint_range(1.0, 40.0) = 10.0;
uniform float ripple_strength : hint_range(0.0, 1.0) = 0.30;
uniform float ripple_speed : hint_range(0.0, 3.0) = 1.0;

// ---------------- 光学
uniform float surface_roughness : hint_range(0.0, 0.5) = 0.05;
uniform float specular_amount : hint_range(0.0, 1.0) = 0.70;
uniform float refraction_strength : hint_range(0.0, 0.06) = 0.012;

// ---------------- 泡沫
uniform vec4 foam_color : source_color = vec4(0.93, 0.96, 0.97, 1.0);
uniform float shore_foam_depth : hint_range(0.0, 1.5) = 0.30;
uniform float crest_foam : hint_range(0.0, 1.0) = 0.05;
uniform float foam_breakup : hint_range(0.0, 1.0) = 0.55;

varying vec3 v_local;      // 本地坐标（平面为 xz）
varying float v_wave;      // 归一化浪高 -1..1
varying vec3 v_axis_x;     // 本地 +X 在视图空间的方向
varying vec3 v_axis_y;     // 本地 +Y
varying vec3 v_axis_z;     // 本地 +Z

// ---------------------------------------------------------------- 噪声
float hash21(vec2 p) {
	p = fract(p * vec2(123.34, 456.21));
	p += dot(p, p + 45.32);
	return fract(p.x * p.y);
}

float vnoise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	vec2 u = f * f * (3.0 - 2.0 * f);
	float a = hash21(i);
	float b = hash21(i + vec2(1.0, 0.0));
	float c = hash21(i + vec2(0.0, 1.0));
	float d = hash21(i + vec2(1.0, 1.0));
	return mix(mix(a, b, u.x), mix(c, d, u.x), u.y);
}

float fbm(vec2 p) {
	return vnoise(p) * 0.60
		+ vnoise(p * 2.05 + vec2(3.1, 1.7)) * 0.27
		+ vnoise(p * 4.10 - vec2(7.3, 2.9)) * 0.13;
}

// 由深度纹理还原视图空间距离
float view_dist(vec2 uv) {
	float d = textureLod(depth_tex, uv, 0.0).r;
	vec3 ndc = vec3(uv * 2.0 - 1.0, d);
	vec4 vp = INV_PROJECTION_MATRIX * vec4(ndc, 1.0);
	vp.xyz /= vp.w;
	return -vp.z;
}

// ---------------------------------------------------------------- 顶点
void vertex() {
	float t = TIME * wave_speed;
	vec2 p = VERTEX.xz;
	float k = 6.2831853 * wave_scale;

	vec2 d1 = normalize(vec2(1.0, 0.35));
	vec2 d2 = normalize(vec2(-0.55, 1.0));
	vec2 d3 = normalize(vec2(0.75, -1.0));

	float a1 = 1.0;
	float a2 = 0.30 + 0.45 * wave_chop;
	float a3 = 0.22 + 0.25 * wave_chop;

	float ph1 = dot(p, d1) * k - t * 1.15;
	float ph2 = dot(p, d2) * k * 1.65 - t * 1.60;
	float ph3 = dot(p, d3) * k * 2.80 - t * 2.05;

	float w = sin(ph1) * a1 + sin(ph2) * a2 + sin(ph3) * a3;
	float norm = a1 + a2 + a3;

	VERTEX.y += wave_height * w;

	// 解析法线：grad(h)
	vec2 grad = d1 * (cos(ph1) * a1 * k)
		+ d2 * (cos(ph2) * a2 * k * 1.65)
		+ d3 * (cos(ph3) * a3 * k * 2.80);
	NORMAL = normalize(vec3(-grad.x * wave_height, 1.0, -grad.y * wave_height));

	v_local = p;
	v_wave = w / norm;

	mat4 mvp = VIEW_MATRIX * MODEL_MATRIX;
	v_axis_x = (mvp * vec4(1.0, 0.0, 0.0, 0.0)).xyz;
	v_axis_y = (mvp * vec4(0.0, 1.0, 0.0, 0.0)).xyz;
	v_axis_z = (mvp * vec4(0.0, 0.0, 1.0, 0.0)).xyz;
}

// ---------------------------------------------------------------- 片元
void fragment() {
	// 细节涟漪梯度
	vec2 q1 = v_local.xz * ripple_scale + vec2(0.30, 0.12) * TIME * ripple_speed;
	vec2 q2 = v_local.xz * ripple_scale * 2.2 - vec2(0.11, 0.28) * TIME * ripple_speed * 0.8;
	float e = 0.35;

	float gx = (fbm(q1 + vec2(e, 0.0)) - fbm(q1)) / e * 0.60
	         + (fbm(q2 + vec2(e, 0.0)) - fbm(q2)) / e * 0.40;
	float gz = (fbm(q1 + vec2(0.0, e)) - fbm(q1)) / e * 0.60
	         + (fbm(q2 + vec2(0.0, e)) - fbm(q2)) / e * 0.40;

	// 把涟漪梯度贴到已位移曲面的切平面上
	vec3 n_geo = normalize(NORMAL);
	vec3 t1 = normalize(v_axis_x - n_geo * dot(v_axis_x, n_geo));
	vec3 t2 = normalize(cross(n_geo, t1));
	float slope = ripple_strength * 0.90;
	vec3 n_view = normalize(n_geo + t1 * (gx * slope) + t2 * (gz * slope));
	NORMAL = n_view;

	// 菲涅尔
	float ndv = clamp(dot(n_view, VIEW), 0.0, 1.0);
	float fres = pow(1.0 - ndv, 5.0);

	// 水体厚度（沿视线）
	float surf_dist = -VERTEX.z;
	float scene_dist = view_dist(SCREEN_UV);
	float thickness = max(scene_dist - surf_dist, 0.0);

	// 屏幕折射：采样到前景物体时回退，避免岸边/遮挡处出错
	vec2 offs = vec2(n_view.x, -n_view.y) * refraction_strength;
	vec2 ruv = clamp(SCREEN_UV + offs, vec2(0.001), vec2(0.999));
	if (view_dist(ruv) < surf_dist) {
		ruv = SCREEN_UV;
	}
	vec3 behind = textureLod(screen_tex, ruv, 0.0).rgb;

	// Beer-Lambert 吸收：越厚越偏深色
	float absorb = 1.0 - exp(-thickness * clarity);
	vec3 body = mix(shallow_color.rgb, deep_color.rgb, absorb);
	float tint_in = smoothstep(0.0, 0.25, thickness);
	vec3 tint = mix(vec3(1.0), body, tint_in);
	vec3 refracted = behind * tint;

	ALBEDO = refracted;
	ALPHA = 1.0;
	ROUGHNESS = surface_roughness;
	SPECULAR = specular_amount;
	METALLIC = 0.0;

	// 菲涅尔：掠射角提高粗糙度，让天空反射更宽而不产生锯齿
	ROUGHNESS = mix(ROUGHNESS, surface_roughness * 2.5 + 0.02, fres);

	// ---------------- 泡沫
	float foam = 0.0;
	if (shore_foam_depth > 0.001) {
		foam = 1.0 - smoothstep(0.0, shore_foam_depth, thickness);
	}
	if (crest_foam > 0.001 && wave_height > 0.001) {
		foam = max(foam, smoothstep(0.55, 0.92, v_wave) * crest_foam);
	}
	float mask = fbm(v_local.xz * ripple_scale * 0.55 + TIME * 0.03 * ripple_speed);
	foam *= mix(1.0, smoothstep(0.30, 0.72, mask), foam_breakup);

	ALBEDO = mix(ALBEDO, foam_color.rgb, foam);
	ROUGHNESS = mix(ROUGHNESS, 0.75, foam);
	SPECULAR = mix(SPECULAR, 0.25, foam);
	EMISSION = foam_color.rgb * foam * 0.12;
}
