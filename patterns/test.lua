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


function main(size)
    a = {}
    b = {}
    st = os.clock()
    for i=0, size-1 do
        a[i] = math.random(size)
    end
    for i=0, size-1 do
        b[i] = math.random(size)
    end
    print("LUA init: "..(os.clock()-st))

    st = os.clock()
    for i=0, size-1 do
        if a[i] ~= b[i] then
            a[i] = a[i] + b[i]
        end
    end
    print("LUA sum: "..(os.clock()-st))
end
