-- Hover helpers used by Styles.inc ------------------------------------------
function GetKey(section, key)
    return SKIN:GetOption(section, key, "255,255,255")
end

function Gsub(input, pattern, replacement)
    -- Strip the trailing alpha added on hover to restore the color.
    return (input:gsub(pattern, replacement or ""))
end

-- App dropdown (opens upward) ------------------------------------------------
local VISIBLE    = 6     -- rows shown (must match MeterAppItem count)
local ITEM_H     = 22
local SELECTOR_Y = 307   -- must match MeterAppSelector's Y in Roku.ini
local GAP        = 2     -- space between list and selector

local ARROW_DOWN = "[\\x25BC]"  -- ▼
local ARROW_UP   = "[\\x25B2]"  -- ▲

local apps     = {}    -- { {id=..., name=...}, ... }
local selected = 0
local offset   = 0
local isOpen   = false
local status   = "Loading apps..."

local function decode(s)
    s = s:gsub("&lt;", "<"):gsub("&gt;", ">"):gsub("&quot;", '"')
         :gsub("&apos;", "'"):gsub("&amp;", "&")
    return s
end

local function select(i)
    selected = i
    if apps[i] then
        SKIN:Bang('!SetVariable', 'SelectedAppId', apps[i].id)
        SKIN:Bang('!UpdateMeter', 'MeterAppGo')
    end
end

local function refresh()
    local n = #apps

    local label = (n > 0 and apps[selected]) and apps[selected].name or status
    SKIN:Bang('!SetOption', 'MeterAppSelector', 'Text', label)
    SKIN:Bang('!SetOption', 'MeterAppArrow', 'Text', isOpen and ARROW_UP or ARROW_DOWN)

    local shown = math.min(VISIBLE, n)
    local top   = SELECTOR_Y - GAP - shown * ITEM_H

    for i = 1, VISIBLE do
        local item = 'MeterAppItem' .. i
        local idx  = offset + i
        local app  = apps[idx]
        if isOpen and app then
            SKIN:Bang('!SetOption', item, 'Y', tostring(top + (i - 1) * ITEM_H))
            SKIN:Bang('!SetOption', item, 'Text', app.name)
            SKIN:Bang('!SetOption', item, 'FontColor',
                      idx == selected and '160,100,255' or '230,230,230')
            SKIN:Bang('!ShowMeter', item)
        else
            SKIN:Bang('!HideMeter', item)
        end
    end

    SKIN:Bang('!UpdateMeterGroup', 'AppList')
    SKIN:Bang('!UpdateMeter', 'MeterAppSelector')
    SKIN:Bang('!UpdateMeter', 'MeterAppArrow')
    SKIN:Bang('!Redraw')
end

function SetStatus(msg)
    status = msg
    if #apps == 0 then refresh() end
end

function ParseApps()
    local measure = SKIN:GetMeasure('MeasureRokuApps')
    local xml = measure and measure:GetStringValue() or ''
    local list = {}

    for attrs, name in xml:gmatch('<app%s+([^>]-)>(.-)</app>') do
        local id = attrs:match('id="([^"]+)"')
        if id then
            table.insert(list, { id = id, name = decode(name) })
        end
    end

    table.sort(list, function(a, b) return a.name:lower() < b.name:lower() end)

    if #list == 0 then
        SetStatus('No apps found')
        return
    end

    local prevId = apps[selected] and apps[selected].id or SKIN:GetVariable('SelectedAppId')
    apps = list
    selected = 1
    for i, a in ipairs(apps) do
        if a.id == prevId then selected = i break end
    end
    offset = math.max(0, math.min(offset, #apps - VISIBLE))
    select(selected)
    refresh()
end

function Toggle()
    if #apps == 0 then return end
    isOpen = not isOpen
    if isOpen then
        if selected <= offset then offset = selected - 1 end
        if selected > offset + VISIBLE then offset = selected - VISIBLE end
        offset = math.max(0, math.min(offset, #apps - VISIBLE))
    end
    refresh()
end

function Scroll(dir)
    offset = math.max(0, math.min(offset + dir, math.max(0, #apps - VISIBLE)))
    refresh()
end

function Cycle(dir)
    if #apps == 0 then return end
    select(((selected - 1 + dir) % #apps) + 1)
    refresh()
end

function Pick(slot)
    local idx = offset + slot
    if apps[idx] then
        select(idx)
        isOpen = false
        refresh()
    end
end
