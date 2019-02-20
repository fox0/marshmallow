function main(bot_state, size)
    local result = {};
    local internal_state = {};

    print(bot_state.a)

    local a = {}
    local b = {}
    local st = os.clock()
    for i = 0, size - 1 do
        a[i] = math.random(size)
    end
    for i = 0, size - 1 do
        b[i] = math.random(size)
    end
    for i = 0, size - 1 do
        if a[i] ~= b[i] then
            a[i] = a[i] + b[i]
        end
    end

    table.insert(result, os.clock() - st)
    internal_state.a = 1;

    return result, internal_state
end
