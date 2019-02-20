--таймаут времени выполнения паттерна (частично реализовано)
timeout = 0.2

--главная функция
---@field bot_state table словарь (key-value) с входными параметрами (только для чтения)
---* и, возможно, другие параметры
---@return table возвращает два значения:
---* todo?
---* и словарь изменившего внутреннего состояния.
function main(bot_state)
    local result = {};
    local internal_state = {};

    if bot_state.myvar == 1 then
        table.insert(result, 'act_wait')
        internal_state.a = 1;
    end

    return result, internal_state
end
