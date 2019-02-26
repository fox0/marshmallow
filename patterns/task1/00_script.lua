timeout = 2.0

priority = 1

input_fields = {
    'size',
}

function main(bot)
    local result = {}

    local a = {}
    local b = {}
    local st = os.clock()
    for i = 0, bot.size - 1 do
        a[i] = math.random(bot.size)
    end
    for i = 0, bot.size - 1 do
        b[i] = math.random(bot.size)
    end
    for i = 0, bot.size - 1 do
        if a[i] ~= b[i] then
            a[i] = a[i] + b[i]
        end
    end

    table.insert(result, os.clock() - st)
    return result, { a = 1 }
end
