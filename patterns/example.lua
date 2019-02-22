--таймаут времени выполнения паттерна (частично реализовано)
timeout = 0.2

--список глобальных переменных, которые будут переданы паттерну в переменную bot_state (частично реализовано)
input_fields = {
    'myvar',
}

output_fields = {
    'a',
}

--главная функция
---@field bot_state table словарь (key-value) с входными параметрами (только для чтения)
---@return table возвращает два значения:
---* список намерений
---* и словарь изменившего внутреннего состояния.
function main(bot_state)
    local result = {}
    local internal_state = {}

    if bot_state.myvar == 1 then
        table.insert(result, 'act_wait')
        internal_state.a = 1
    end

    return result, internal_state
end
