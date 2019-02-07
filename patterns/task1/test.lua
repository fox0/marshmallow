function main(size)
    a = {}
    b = {}
    st = os.clock()
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
    return os.clock() - st
end
