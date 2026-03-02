VERTEX_SHADER_2D = """
#version 330
in vec2 in_pos;
in vec2 in_texcoord;
out vec2 v_texcoord;
void main() {
    gl_Position = vec4(in_pos, 0.0, 1.0);
    v_texcoord = in_texcoord;
}
"""
FRAGMENT_SHADER_2D = """
#version 330
uniform sampler2D u_texture;
in vec2 v_texcoord;
out vec4 f_color;
void main() {
    f_color = texture(u_texture, v_texcoord);
}
"""