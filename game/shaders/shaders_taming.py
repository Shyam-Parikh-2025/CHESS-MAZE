VERTEX_SHADER = """
#version 330

in vec3 in_pos;
in vec3 in_translate;
in vec2 in_texcoord;

uniform mat4 u_projection;
uniform mat4 u_view;

out vec2 v_texcoord;

void main() {
    vec4 world_pos = vec4(in_pos + in_translate, 1.0);
    gl_Position = u_projection * u_view * world_pos;
    v_texcoord = in_texcoord;
}
"""
FRAGMENT_SHADER = """
#version 330
uniform sampler2D u_texture;
in vec2 v_texcoord;
out vec4 f_color;
void main() {
    f_color = texture(u_texture, v_texcoord);
}
"""