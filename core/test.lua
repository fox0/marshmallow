--Файл написан для теста TestLunaCodeFile

timeout = 0.2

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
    return result, internal_state
end
