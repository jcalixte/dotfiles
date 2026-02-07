return {
  {
    "stevearc/conform.nvim",
    event = "BufWritePre",
    opts = require "configs.conform",
  },

  {
    "neovim/nvim-lspconfig",
    config = function()
      require "configs.lspconfig"
    end,
  },

  -- Markdown notebook: link completion, follow, rename
  {
    "jakewvincent/mkdnflow.nvim",
    ft = { "markdown" },
    config = function()
      require "configs.mkdnflow"
    end,
  },

  -- Async linting (markdownlint-cli2)
  {
    "mfussenegger/nvim-lint",
    event = { "BufReadPre", "BufNewFile" },
    config = function()
      require "configs.lint"
    end,
  },

  -- File explorer (buffer-based, rename-friendly)
  {
    "stevearc/oil.nvim",
    lazy = false,
    config = function()
      require("oil").setup {
        default_file_explorer = true,
        view_options = {
          show_hidden = true,
        },
      }
    end,
  },

  -- Load custom VS Code snippets from ~/.config/nvim/snippets/
  {
    "L3MON4D3/LuaSnip",
    opts = function(_, opts)
      local paths = vim.g.vscode_snippets_path or {}
      if type(paths) == "string" then
        paths = { paths }
      end
      table.insert(paths, vim.fn.stdpath "config" .. "/snippets")
      vim.g.vscode_snippets_path = paths
      return opts
    end,
  },

  -- Add mkdnflow as nvim-cmp source for markdown files
  {
    "hrsh7th/nvim-cmp",
    opts = function(_, opts)
      local cmp = require "cmp"
      -- Add mkdnflow source for markdown
      cmp.setup.filetype("markdown", {
        sources = cmp.config.sources({
          { name = "mkdnflow" },
          { name = "luasnip" },
          { name = "path" },
        }, {
          { name = "buffer" },
        }),
      })
      return opts
    end,
  },
}
