require "nvchad.mappings"

-- add yours here

local map = vim.keymap.set

map("n", ";", ":", { desc = "CMD enter command mode" })
map("n", "<c-z>", "<nop>")
map("i", "jj", "<Esc>", { desc = "Exit insert mode with jj", noremap = true, silent = true })

-- map({ "n", "i", "v" }, "<C-s>", "<cmd> w <cr>")
map('n', '<C-M-t>', ':lua CloseOtherBuffers()<CR>', { noremap = true, silent = true })

-- Oil file explorer
map("n", "-", "<cmd>Oil<CR>", { desc = "Open parent directory in Oil" })

function CloseOtherBuffers()
  local current = vim.fn.bufnr('%')
  for _, bufnr in ipairs(vim.fn.getbufinfo({ buflisted = 1 })) do
    if bufnr.bufnr ~= current then
      vim.api.nvim_buf_delete(bufnr.bufnr, { force = true })
    end
  end
end
