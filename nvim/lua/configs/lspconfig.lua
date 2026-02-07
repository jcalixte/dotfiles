-- load NvChad defaults (sets capabilities, on_init, diagnostics)
require("nvchad.configs.lspconfig").defaults()

-- enable servers with default config (Neovim 0.11+ native API)
vim.lsp.enable { "html", "cssls", "ts_ls" }
