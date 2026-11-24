-- Minimal script to support Styles.inc hover logic
function GetKey(section, key)
    return SKIN:GetOption(section, key, "255,255,255")
end

function Gsub(input, pattern, replacement)
    -- Simply returns a dummy value to satisfy the style's color reset logic
    return input:gsub(pattern, replacement)
end