import numpy as np
from rio_color.operations import parse_operations

def apply_rio_color(ops, channel, c_red, c_green, c_blue):
    arr = np.stack([np.clip(c_red, 0, 1), 
                    np.clip(c_green, 0, 1), 
                    np.clip(c_blue, 0, 1)], axis=0)
    assert arr.shape[0] == 3
    assert np.nanmin(arr) >= 0, "Input values must be >= 0"
    assert np.nanmax(arr) <= 1, "Input values must be <= 1"
    for func in parse_operations(ops):
        arr = func(arr)
    return (arr[channel, :, :] * 255).astype(np.uint8)

def apply_rio_color_red(c_red, c_green, c_blue):
    return apply_rio_color(0, c_red, c_green, c_blue)

def apply_rio_color_green(c_red, c_green, c_blue):
    return apply_rio_color(1, c_red, c_green, c_blue)

def apply_rio_color_blue(c_red, c_green, c_blue):
    return apply_rio_color(2, c_red, c_green, c_blue)