VERTEX_SHADER_3D = """
#version 330 core
in vec3 in_pos;
in vec2 in_texcoord;
out vec2 v_texcoord;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_model;

void main() {
    v_texcoord = in_texcoord;
    gl_Position = m_proj * m_view * m_model * vec4(in_pos, 1.0);
}
"""

FRAGMENT_SHADER_3D = """
#version 330 core
in vec2 v_texcoord;
out vec4 f_color;

uniform sampler2D u_texture;
uniform vec3 u_color;

void main() {
    f_color = vec4(u_color, 1.0);
}
"""