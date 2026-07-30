-- Bad Apple terminal renderer.
-- Reads raw 8-bit grayscale frames from stdin and writes a PGM image stream.
-- Compatible with Lua 5.3+ and LuaTeX's --luaonly mode.

local cols = tonumber(arg[1]) or 76
local rows = tonumber(arg[2]) or 40
local fps = tonumber(arg[3]) or 8

local width, height = 480, 360
local cell_w, cell_h = 5, 7
local video_x, video_y = 50, 40
local video_w, video_h = cols * cell_w, rows * cell_h
assert(video_w == 380 and video_h == 280, "renderer expects 76x40 source frames")

io.stdin:setvbuf("no")
io.stdout:setvbuf("no")

local FONT = {
  [" "]={"00000","00000","00000","00000","00000","00000","00000"},
  ["A"]={"01110","10001","10001","11111","10001","10001","10001"},
  ["B"]={"11110","10001","10001","11110","10001","10001","11110"},
  ["C"]={"01110","10001","10000","10000","10000","10001","01110"},
  ["D"]={"11110","10001","10001","10001","10001","10001","11110"},
  ["E"]={"11111","10000","10000","11110","10000","10000","11111"},
  ["F"]={"11111","10000","10000","11110","10000","10000","10000"},
  ["G"]={"01110","10001","10000","10111","10001","10001","01110"},
  ["H"]={"10001","10001","10001","11111","10001","10001","10001"},
  ["I"]={"11111","00100","00100","00100","00100","00100","11111"},
  ["J"]={"00111","00010","00010","00010","10010","10010","01100"},
  ["K"]={"10001","10010","10100","11000","10100","10010","10001"},
  ["L"]={"10000","10000","10000","10000","10000","10000","11111"},
  ["M"]={"10001","11011","10101","10101","10001","10001","10001"},
  ["N"]={"10001","11001","10101","10011","10001","10001","10001"},
  ["O"]={"01110","10001","10001","10001","10001","10001","01110"},
  ["P"]={"11110","10001","10001","11110","10000","10000","10000"},
  ["Q"]={"01110","10001","10001","10001","10101","10010","01101"},
  ["R"]={"11110","10001","10001","11110","10100","10010","10001"},
  ["S"]={"01111","10000","10000","01110","00001","00001","11110"},
  ["T"]={"11111","00100","00100","00100","00100","00100","00100"},
  ["U"]={"10001","10001","10001","10001","10001","10001","01110"},
  ["V"]={"10001","10001","10001","10001","10001","01010","00100"},
  ["W"]={"10001","10001","10001","10101","10101","10101","01010"},
  ["X"]={"10001","10001","01010","00100","01010","10001","10001"},
  ["Y"]={"10001","10001","01010","00100","00100","00100","00100"},
  ["Z"]={"11111","00001","00010","00100","01000","10000","11111"},
  ["0"]={"01110","10001","10011","10101","11001","10001","01110"},
  ["1"]={"00100","01100","00100","00100","00100","00100","01110"},
  ["2"]={"01110","10001","00001","00010","00100","01000","11111"},
  ["3"]={"11110","00001","00001","01110","00001","00001","11110"},
  ["4"]={"00010","00110","01010","10010","11111","00010","00010"},
  ["5"]={"11111","10000","10000","11110","00001","00001","11110"},
  ["6"]={"01110","10000","10000","11110","10001","10001","01110"},
  ["7"]={"11111","00001","00010","00100","01000","01000","01000"},
  ["8"]={"01110","10001","10001","01110","10001","10001","01110"},
  ["9"]={"01110","10001","10001","01111","00001","00001","01110"},
  ["."]={"00000","00000","00000","00000","00000","00110","00110"},
  [":"]={"00000","00100","00100","00000","00100","00100","00000"},
  ["-"]={"00000","00000","00000","11111","00000","00000","00000"},
  ["="]={"00000","00000","11111","00000","11111","00000","00000"},
  ["+"]={"00000","00100","00100","11111","00100","00100","00000"},
  ["*"]={"00000","10101","01110","11111","01110","10101","00000"},
  ["#"]={"01010","11111","01010","01010","11111","01010","00000"},
  ["%"]={"11001","11010","00100","01000","10110","00110","00000"},
  ["@"]={"01110","10001","10111","10101","10111","10000","01110"},
  ["_"]={"00000","00000","00000","00000","00000","00000","11111"},
  ["|"]={"00100","00100","00100","00100","00100","00100","00100"},
  ["$"]={"00100","01111","10100","01110","00101","11110","00100"},
  ["~"]={"00000","00000","01001","10110","00000","00000","00000"},
}

local ramp = {" ", ".", ":", "-", "=", "+", "*", "#", "%", "@"}
local black, white = string.char(0), string.char(255)
local glyph_rows = {}
for ch, pattern in pairs(FONT) do
  glyph_rows[ch] = {}
  for y = 1, 7 do
    local parts = {}
    for x = 1, 5 do
      parts[x] = pattern[y]:sub(x, x) == "1" and white or black
    end
    glyph_rows[ch][y] = table.concat(parts)
  end
end

local canvas = {}
for y = 1, height do
  canvas[y] = {}
  for x = 1, width do canvas[y][x] = 0 end
end

local function set_pixel(x, y, value)
  if x >= 1 and x <= width and y >= 1 and y <= height then canvas[y][x] = value end
end

local function draw_text(text, x0, y0)
  local x = x0
  for i = 1, #text do
    local ch = text:sub(i, i)
    local pattern = FONT[ch] or FONT[" "]
    for gy = 1, 7 do
      for gx = 1, 5 do
        if pattern[gy]:sub(gx, gx) == "1" then set_pixel(x + gx - 1, y0 + gy - 1, 255) end
      end
    end
    x = x + 6
  end
end

-- Static terminal chrome.
draw_text("DESERVETO@GITHUB:~$ LUA BAD_APPLE.LUA", 12, 10)
draw_text("LUA ASCII RENDERER | SILENT | LOOP", 12, 342)
for x = 45, 435 do set_pixel(x, 35, 255); set_pixel(x, 325, 255) end
for y = 35, 325 do set_pixel(45, y, 255); set_pixel(435, y, 255) end

local static_rows = {}
for y = 1, height do
  local bytes = {}
  for x = 1, width do bytes[x] = string.char(canvas[y][x]) end
  static_rows[y] = table.concat(bytes)
end

local pgm_header = string.format("P5\n%d %d\n255\n", width, height)
local frame_bytes = cols * rows
local frame_count = 0

while true do
  local frame = io.stdin:read(frame_bytes)
  if not frame or #frame < frame_bytes then break end
  frame_count = frame_count + 1
  io.write(pgm_header)

  for y = 1, height do
    if y >= video_y and y < video_y + video_h then
      local source_y = math.floor((y - video_y) / cell_h)
      local glyph_y = ((y - video_y) % cell_h) + 1
      local parts = {static_rows[y]:sub(1, video_x - 1)}
      local offset = source_y * cols
      for source_x = 1, cols do
        local value = frame:byte(offset + source_x)
        local normalized = value / 255
        local index = math.floor((normalized ^ 0.90) * (#ramp - 1) + 0.5) + 1
        if index < 1 then index = 1 elseif index > #ramp then index = #ramp end
        parts[#parts + 1] = glyph_rows[ramp[index]][glyph_y]
      end
      parts[#parts + 1] = static_rows[y]:sub(video_x + video_w)
      io.write(table.concat(parts))
    else
      io.write(static_rows[y])
    end
  end
end

io.stderr:write(string.format("Rendered %d frames at %d FPS\n", frame_count, fps))
