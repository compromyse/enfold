--- Set Up Lspconfig
local lspconfig = require('lspconfig')
local capabilities = require('cmp_nvim_lsp').default_capabilities()
lspconfig['vtsls'].setup {
  capabilities = capabilities
}

lspconfig['pyright'].setup {
  capabilities = capabilities
}
