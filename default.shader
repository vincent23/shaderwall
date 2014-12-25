#ifdef GL_ES
precision mediump float;
#endif
uniform float time;
uniform vec2 resolution;

// Colors
vec3 BACKGROUND_BASE = vec3(0.0, 0.0, 0.0);
vec3 CIRCLE = vec3(1.0, 1.0, 1.0);
vec3 BEAM = vec3(1.0, 1.0, 1.0);
vec3 BEAM_SHADOW = vec3(1.0, 0.63, 0.0);
vec3 BLOCK_0 = vec3(0.25, 0.08, 0.36);
vec3 BLOCK_1 = vec3(0.43, 0.31, 0.71);
vec3 BLOCK_2 = vec3(1.0, 0.63, 0.0);
vec3 BLOCK_3 = vec3(1.0, 0.50, 0.20);
vec3 BLOCK_4 = vec3(1.0, 0.35, 0.27);

float SCALE = resolution.y / 16.0;

// Offsets (as fractions)
float BLOCK_OFFSET = 1.0 * (SCALE / resolution.y);
float LOGO_OFFSET = 1.25 * (SCALE / resolution.y);

// Circle smoothing
float SMOOTHING = 0.25;

// Time based fade-in (used for beam animation)
float fadein(float x, float delay, float speed) {
    if((time*speed) < delay) {
        return 0.0;
    }else if(((time*speed)-delay) < 1.6) {
        return x*abs(sin((time*speed)-delay));
    } else {
        return x;
    }
}

// Time based pulse (used for beam animation)
float pulse(float x, float delay, float speed) {
    if((time*speed) < delay) {
        return 0.0;
    }else {
        return x*abs(sin((time*speed)-delay));
    }

}

// Check for block boundaries
bool check_block_boundaries(vec2 diff, int box) {
    return (
        diff.x <= SCALE/2.0 && // left side
        diff.x >= -SCALE/2.0 && // right side
        diff.y+(resolution.y*BLOCK_OFFSET) <= -SCALE*(0.0+float(box)) && // bottom side
        diff.y+(resolution.y*BLOCK_OFFSET) > -SCALE*(1.0+float(box)) // top side
    );
}

// Check for boundaries of cut in top of circle (3x the width of the blocks)
bool is_cut(vec2 center, vec2 diff) {
    return !(
        gl_FragCoord.y < center.y || // top of circle
        diff.x > SCALE*1.5 || // left side
        diff.x < -SCALE*1.5 // right side
    );
}

// Calculate circle intensity
float is_circle(vec2 position) {
    float current_radius = length(position);
    float edge0 = SCALE / (4.0*resolution.y); // lower edge
    float edge1 = (2.+SMOOTHING/2.) * edge0; // upper edge
    float x = abs(current_radius - (4.0 - 2.0*SMOOTHING)*(SCALE / resolution.y));
    return 1.0 - smoothstep(edge0, edge1, x);
}

// Check for beam intensity
float is_beam_shadow(vec2 position) {
    float scalefix = resolution.y / SCALE / 16.0;

    position.y -= 2.5 * BLOCK_OFFSET + SCALE / resolution.y;
    float edge0 = 0.9;
    float edge1 = 1.0;
    float x = 1.0 - abs(position.x/6.0)*scalefix - abs(position.y*5.0)*scalefix;
    x = fadein(x,0.0,1.0);
    return smoothstep(edge0, edge1, x);
}

// Check for beam
float is_beam(vec2 position) {
    float scalefix = resolution.y / SCALE / 16.0;

    position.y -= 2.5 * BLOCK_OFFSET + SCALE / resolution.y;
    float edge0;
    float edge1;
    float x;

    edge0 = 0.0;
    edge1 = 1.0;
    x = 1.0 - pow(abs(position.x), 2.0)*220.0*scalefix - abs(position.y*34.0*scalefix);
    x = x * 2.0;
    x = pulse(x,1.0,0.8);
    float beam_part1 = smoothstep(edge0, edge1, x);

    edge0 = 0.4;
    edge1 = 0.7;
    x = 1.0 - abs(position.x/1.0)*scalefix - abs(position.y*256.0*scalefix);
    x = fadein(x,1.5,0.8);
    float beam_part2 = smoothstep(edge0, edge1, x);

    return beam_part1 + beam_part2;
}

void main(void) {
    // Calculate (absolute) position including offsets for circle
    vec2 position = gl_FragCoord.xy / resolution.yy;
    position.x -= 0.5 / resolution.y * resolution.x;
    position.y -= 0.5;
    position.y += LOGO_OFFSET;

    // The center of the circle
    vec2 center = vec2(resolution.x/2.0, resolution.y/2.0 - LOGO_OFFSET * resolution.y);

    // How far we are from the center
    float radius=length(gl_FragCoord.xy-center);

    // Calculate (relative) position between center of circle and current pixel
    vec2 diff = center-gl_FragCoord.xy;

    // Create blocks (from bottom to top)
    if(check_block_boundaries(diff, 0)) BACKGROUND_BASE = BLOCK_0;
    if(check_block_boundaries(diff, 1)) BACKGROUND_BASE = BLOCK_1;
    if(check_block_boundaries(diff, 2)) BACKGROUND_BASE = BLOCK_2;
    if(check_block_boundaries(diff, 3)) BACKGROUND_BASE = BLOCK_3;
    if(check_block_boundaries(diff, 4)) BACKGROUND_BASE = BLOCK_4;


    // Draw beam shadow
    BACKGROUND_BASE = mix(BACKGROUND_BASE, BEAM_SHADOW, is_beam_shadow(position));

    // Draw beam
    BACKGROUND_BASE = mix(BACKGROUND_BASE, BEAM, is_beam(position));

    // Draw circle
    if (!is_cut(center,diff)) {
        // mix color between background-color and circle-color
        BACKGROUND_BASE = mix(BACKGROUND_BASE, CIRCLE * resolution.y, is_circle(position));
        gl_FragColor = vec4( BACKGROUND_BASE , 1.);
    }

    gl_FragColor = vec4( BACKGROUND_BASE , 1.);
}





