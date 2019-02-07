--Lua is a language as dynamic as Python, but LuaJIT compiles it to very fast machine code,
--sometimes faster than many statically compiled languages for computational code.
--end The language runtime is very small and carefully designed for embedding.

--список устройств (необязательно)
dev = {
    'coord',
    'motor',
}

--список паттернов (необязательно)
requirements_pattern = {
    'common',
}

--todo дерево зависимостей паттернов? Общая память? Очереди/капалы между паттернами?

--главная функция. Должна вернуть todo (?)
function main()
    return nil
end
