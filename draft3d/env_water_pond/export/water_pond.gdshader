// env_water_pond - 低多边形水面着色器（Godot 4.x）
// 配套 export/env_water_pond.glb 使用：材质槽 0（水面）挂本 shader，材质槽 1（泡沫带）保留纯色或设为白色。
// 特性：菲涅尔、屏幕折射扰动、两层程序噪声法线滚动、深度差岸边泡沫、顶点波浪（保留硬边）。
shader_type spatial;
render_mode blend_mix, depth_draw_opaque, cull_disabled, diffuse_burley, specular_schlick_ggx;

// ----------------------------- 贴图
uniform sampler2D screen_tex : hint_screen_texture, filter_linear_mipmap;
uniform sampler2D depth_tex : hint_depth_texture, filter_linear_mipmap, repeat_disable;

// ----------------------------- 颜色
uniform vec4 shallow_color : source_color = vec4(0.247, 0.663, 0.627, 1.0); // #3FA9A0
uniform vec4 deep_color : source_color = vec4(0.094, 0.373, 0.412, 1.0);    // 深水偏蓝
uniform vec4 foam_color : source_color = vec4(0.863, 0.937, 0.949, 1.0);    // #DCEFEF
uniform float surface_alpha : hint_range(0.0, 1.0) = 1.0;

// ----------------------------- 菲涅尔
uniform float fresnel_power : hint_range(1.0, 12.0) = 5.0;
uniform float fresnel_max : hint_range(0.0, 1.0) = 0.92;

// ----------------------------- 折射
uniform float refraction_strength : hint_range(0.0, 0.08) = 0.018;
uniform float refraction_tint : hint_range(0.0, 1.0) = 0.45;

// ----------------------------- 程序噪声法线
uniform float noise_scale : hint_range(0.5, 12.0) = 3.2;
uniform float normal_scale : hint_range(0.0, 1.0) = 0.22;
uniform float flow_speed : hint_range(0.0, 4.0) = 1.0;

// ----------------------------- 顶点波浪（本地坐标，平铺周期 = tile_size）
uniform float tile_size : hint_range(1.0, 32.0) = 4.0;
uniform float wave_amp : hint_range(0.0, 0.03) = 0.025;
uniform float wave_speed : hint_range(0.0, 4.0) = 1.0;

// ----------------------------- 岸边泡沫（需要水下有可见的池底网格才有意义）
uniform bool shore_foam_enabled = true;
uniform float foam_depth : hint_range(0.02, 1.0) = 0.25;
uniform float foam_breakup : hint_range(0.0, 1.0) = 0.55;

// ----------------------------- 镜面
uniform float water_roughness : hint_range(0.0, 0.6) = 0.06;
uniform float water_specular : hint_range(0.0, 1.0) = 0.75;

const float TAU = 6.28318530718;

// ----------------------------- 传递
varying vec2 v_local;      // 本地平面坐标 / tile_size，平铺后周期为 1
varying vec3 v_dir_x;      // 视图空间：本地 +X 方向
varying vec3 v_dir_z;      // 视图空间：本地 +Z 方向
varying vec3 v_dir_y;      // 视图空间：本地 +Y（向上）

// ----------------------------- 噪声
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
	return vnoise(p) * 0.62
		+ vnoise(p * 2.07 + vec2(3.1, 1.7)) * 0.26
		+ vnoise(p * 4.13 - vec2(7.3, 2.9)) * 0.12;
}

void vertex() {
	// 位移：波数取整数，保证 4m 周期拼接无缝；幅度上限 3cm 以保留低多边形硬边
	float t = TIME * wave_speed;
	vec2 g = VERTEX.xz / tile_size;
	float w = sin(TAU * (1.0 * g.x + 1.0 * g.y) - t * 1.0)
			+ sin(TAU * (2.0 * g.x - 1.0 * g.y) - t * 1.45)
			+ sin(TAU * (1.0 * g.x + 3.0 * g.y) - t * 1.90);
	VERTEX.y += wave_amp * w / 3.0;

	// 传递平面坐标（未位移前采样，避免平铺接缝随波浪漂移）
	v_local = vec2(VERTEX.x, VERTEX.z) / tile_size;

	// 本地坐标轴在视图空间的方向（在顶点里算，避开片元矩阵歧义）
	mat4 mvp = VIEW_MATRIX * MODEL_MATRIX;
	v_dir_x = (mvp * vec4(1.0, 0.0, 0.0, 0.0)).xyz;
	v_dir_y = (mvp * vec4(0.0, 1.0, 0.0, 0.0)).xyz;
	v_dir_z = (mvp * vec4(0.0, 0.0, 1.0, 0.0)).xyz;
}

void fragment() {
	// ---------------- 两层不同速度 / 尺度的噪声法线
	vec2 flow1 = vec2(0.0130, 0.0085) * TIME * flow_speed;
	vec2 flow2 = vec2(-0.0075, 0.0110) * TIME * flow_speed;
	vec2 p1 = v_local * noise_scale + flow1;
	vec2 p2 = v_local * noise_scale * 2.35 + flow2;

	float e = 0.012;
	float n1 = fbm(p1);
	float n1x = fbm(p1 + vec2(e, 0.0));
	float n1z = fbm(p1 + vec2(0.0, e));
	float n2 = fbm(p2);
	float n2x = fbm(p2 + vec2(e, 0.0));
	float n2z = fbm(p2 + vec2(0.0, e));

	vec2 grad = vec2(n1x - n1, n1z - n1) / e * 0.65
			  + vec2(n2x - n2, n2z - n2) / e * 0.45;

	vec3 n_local = normalize(vec3(-grad.x * normal_scale, 1.0, -grad.y * normal_scale));

	// 本地法线 -> 视图空间
	vec3 tx = normalize(v_dir_x);
	vec3 ty = normalize(v_dir_y);
	vec3 tz = normalize(v_dir_z);
	vec3 n_view = normalize(n_local.x * tx + n_local.y * ty + n_local.z * tz);

	NORMAL = n_view;

	// ---------------- 菲涅尔
	float ndv = clamp(dot(n_view, VIEW), 0.0, 1.0);
	float fres = pow(1.0 - ndv, fresnel_power) * fresnel_max;

	// ---------------- 屏幕折射（轻微扰动 + 水色染色）
	vec2 refr_uv = SCREEN_UV + n_view.xy * refraction_strength;
	vec3 behind = textureLod(screen_tex, clamp(refr_uv, vec2(0.001), vec2(0.999)), 0.0).rgb;
	vec3 water_tint = mix(deep_color.rgb, shallow_color.rgb, clamp(ndv, 0.0, 1.0));
	vec3 refracted = mix(behind * water_tint, behind, 1.0 - refraction_tint);

	// 掠射角往天空色（浅白青）偏移
	vec3 grazing = mix(shallow_color.rgb, foam_color.rgb, 0.45);
	ALBEDO = mix(refracted, grazing, fres);
	ALPHA = surface_alpha;
	ROUGHNESS = water_roughness;
	METALLIC = 0.0;
	SPECULAR = water_specular;

	// ---------------- 岸边泡沫（深度差）
	float foam = 0.0;
	if (shore_foam_enabled) {
		float depth_raw = textureLod(depth_tex, SCREEN_UV, 0.0).r;
		vec3 ndc = vec3(SCREEN_UV * 2.0 - 1.0, depth_raw);
		vec4 view_pos = INV_PROJECTION_MATRIX * vec4(ndc, 1.0);
		view_pos.xyz /= view_pos.w;
		float scene_dist = -view_pos.z;

		// VERTEX 在片元里是视图空间坐标
		float surface_dist = -VERTEX.z;
		float diff = scene_dist - surface_dist;
		float shore = 1.0 - smoothstep(0.0, foam_depth, max(diff, 0.0));

		// 泡沫破碎：噪声 + 缓慢流动
		float breakup = fbm(v_local * noise_scale * 3.4 + flow1 * 2.0);
		shore *= mix(1.0, smoothstep(0.25, 0.75, breakup), foam_breakup);

		foam = clamp(shore, 0.0, 1.0);
	}

	ALBEDO = mix(ALBEDO, foam_color.rgb, foam);
	ROUGHNESS = mix(ROUGHNESS, 0.62, foam);
	SPECULAR = mix(SPECULAR, 0.30, foam);

	// 泡沫略微自发光，避免背光时消失
	EMISSION = foam_color.rgb * foam * 0.15;
}
