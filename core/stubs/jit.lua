--http://luajit.org/ext_jit.html

jit = {}
jit.os = ''
jit.arch = ''
jit.version = ''
jit.version_num = 0

---@return boolean, string, string
function jit.status()
end

--todo
function jit.on()
end

function jit.off()
end

function jit.flush()
end

function jit.attach()
end

local opt = {}
jit.opt = opt

function opt.start()
end
