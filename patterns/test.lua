--Lua is a language as dynamic as Python, but LuaJIT compiles it to very fast machine code,
--sometimes faster than many statically compiled languages for computational code.
--end The language runtime is very small and carefully designed for embedding.


--dev {
--    #coord_x
--    #coord_y
--}
--
--## Блок с кодом паттерна
--code {
--    #act 'stop', 0.5
--}



ss = 5

function run(a)
    return a + ss
end

a, b, c = python.eval("(1,2)")
