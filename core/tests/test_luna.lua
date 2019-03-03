--  Copyright (c) 2019. fox0 https://github.com/fox0/

timeout = 0.2

priority = 1

input_fields = {
    'var',
}

output_fields = {
    'a',
}

function main(bot_state)
    local result = {}
    local internal_state = {}
    if bot_state.var == 1 then
        internal_state.a = 1
    end
    table.insert(result, 42)
    return result, internal_state
end
