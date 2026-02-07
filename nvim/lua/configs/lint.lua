local lint = require "lint"

lint.linters_by_ft = {
  markdown = { "markdownlint-cli2" },
}

-- Lint on save and when opening a file
vim.api.nvim_create_autocmd({ "BufWritePost", "BufReadPost" }, {
  callback = function()
    lint.try_lint()
  end,
})
