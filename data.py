bd = {
  "schema": "BD_Vendas",
  "tables": [
    {
      "name": "Categoria",
      "columns": [
        { "name": "idCategoria", "type": "INT", "nullable": False, "isPrimaryKey": True },
        { "name": "Descricao", "type": "VARCHAR(45)", "nullable": False, "isPrimaryKey": False }
      ],
      "foreignKeys": []
    },
    {
      "name": "Produto",
      "columns": [
        { "name": "idProduto", "type": "INT", "nullable": False, "isPrimaryKey": True },
        { "name": "Nome", "type": "VARCHAR(45)", "nullable": False, "isPrimaryKey": False },
        { "name": "Descricao", "type": "VARCHAR(200)", "nullable": True, "isPrimaryKey": False },
        { "name": "Preco", "type": "DECIMAL(18,2)", "nullable": False, "default": "0", "isPrimaryKey": False },
        { "name": "QuantEstoque", "type": "DECIMAL(10,2)", "nullable": False, "default": "0", "isPrimaryKey": False },
        { "name": "Categoria_idCategoria", "type": "INT", "nullable": False, "isPrimaryKey": False }
      ],
      "foreignKeys": [
        { "column": "Categoria_idCategoria", "referencesTable": "Categoria", "referencesColumn": "idCategoria" }
      ]
    },
    {
      "name": "TipoCliente",
      "columns": [
        { "name": "idTipoCliente", "type": "INT", "nullable": False, "isPrimaryKey": True },
        { "name": "Descricao", "type": "VARCHAR(45)", "nullable": True, "isPrimaryKey": False }
      ],
      "foreignKeys": []
    },
    {
      "name": "Cliente",
      "columns": [
        { "name": "idCliente", "type": "INT", "nullable": False, "isPrimaryKey": True },
        { "name": "Nome", "type": "VARCHAR(45)", "nullable": False, "isPrimaryKey": False },
        { "name": "Email", "type": "VARCHAR(100)", "nullable": False, "isPrimaryKey": False },
        { "name": "Nascimento", "type": "DATETIME", "nullable": True, "isPrimaryKey": False },
        { "name": "Senha", "type": "VARCHAR(200)", "nullable": True, "isPrimaryKey": False },
        { "name": "TipoCliente_idTipoCliente", "type": "INT", "nullable": False, "isPrimaryKey": False },
        { "name": "DataRegistro", "type": "DATETIME", "nullable": False, "default": "Now()", "isPrimaryKey": False }
      ],
      "foreignKeys": [
        { "column": "TipoCliente_idTipoCliente", "referencesTable": "TipoCliente", "referencesColumn": "idTipoCliente" }
      ]
    },
    {
      "name": "TipoEndereco",
      "columns": [
        { "name": "idTipoEndereco", "type": "INT", "nullable": False, "isPrimaryKey": True },
        { "name": "Descricao", "type": "VARCHAR(45)", "nullable": False, "isPrimaryKey": False }
      ],
      "foreignKeys": []
    },
    {
      "name": "Endereco",
      "columns": [
        { "name": "idEndereco", "type": "INT", "nullable": False, "isPrimaryKey": True },
        { "name": "EnderecoPadrao", "type": "TINYINT", "nullable": False, "default": "0", "isPrimaryKey": False },
        { "name": "Logradouro", "type": "VARCHAR(45)", "nullable": True, "isPrimaryKey": False },
        { "name": "Numero", "type": "VARCHAR(45)", "nullable": True, "isPrimaryKey": False },
        { "name": "Complemento", "type": "VARCHAR(45)", "nullable": True, "isPrimaryKey": False },
        { "name": "Bairro", "type": "VARCHAR(45)", "nullable": True, "isPrimaryKey": False },
        { "name": "Cidade", "type": "VARCHAR(45)", "nullable": True, "isPrimaryKey": False },
        { "name": "UF", "type": "VARCHAR(2)", "nullable": True, "isPrimaryKey": False },
        { "name": "CEP", "type": "VARCHAR(8)", "nullable": True, "isPrimaryKey": False },
        { "name": "TipoEndereco_idTipoEndereco", "type": "INT", "nullable": False, "isPrimaryKey": False },
        { "name": "Cliente_idCliente", "type": "INT", "nullable": False, "isPrimaryKey": False }
      ],
      "foreignKeys": [
        { "column": "TipoEndereco_idTipoEndereco", "referencesTable": "TipoEndereco", "referencesColumn": "idTipoEndereco" },
        { "column": "Cliente_idCliente", "referencesTable": "Cliente", "referencesColumn": "idCliente" }
      ]
    },
    {
      "name": "Telefone",
      "columns": [
        { "name": "Numero", "type": "VARCHAR(42)", "nullable": False, "isPrimaryKey": True },
        { "name": "Cliente_idCliente", "type": "INT", "nullable": False, "isPrimaryKey": True }
      ],
      "foreignKeys": [
        { "column": "Cliente_idCliente", "referencesTable": "Cliente", "referencesColumn": "idCliente" }
      ]
    },
    {
      "name": "Status",
      "columns": [
        { "name": "idStatus", "type": "INT", "nullable": False, "isPrimaryKey": True },
        { "name": "Descricao", "type": "VARCHAR(45)", "nullable": False, "isPrimaryKey": False }
      ],
      "foreignKeys": []
    },
    {
      "name": "Pedido",
      "columns": [
        { "name": "idPedido", "type": "INT", "nullable": False, "isPrimaryKey": True },
        { "name": "Status_idStatus", "type": "INT", "nullable": False, "isPrimaryKey": False },
        { "name": "DataPedido", "type": "DATETIME", "nullable": False, "default": "Now()", "isPrimaryKey": False },
        { "name": "ValorTotalPedido", "type": "DECIMAL(18,2)", "nullable": False, "default": "0", "isPrimaryKey": False },
        { "name": "Cliente_idCliente", "type": "INT", "nullable": False, "isPrimaryKey": False }
      ],
      "foreignKeys": [
        { "column": "Status_idStatus", "referencesTable": "Status", "referencesColumn": "idStatus" },
        { "column": "Cliente_idCliente", "referencesTable": "Cliente", "referencesColumn": "idCliente" }
      ]
    },
    {
      "name": "Pedido_has_Produto",
      "columns": [
        { "name": "idPedidoProduto", "type": "INT", "nullable": False, "isPrimaryKey": True, "autoIncrement": True },
        { "name": "Pedido_idPedido", "type": "INT", "nullable": False, "isPrimaryKey": False },
        { "name": "Produto_idProduto", "type": "INT", "nullable": False, "isPrimaryKey": False },
        { "name": "Quantidade", "type": "DECIMAL(10,2)", "nullable": False, "isPrimaryKey": False },
        { "name": "PrecoUnitario", "type": "DECIMAL(18,2)", "nullable": False, "isPrimaryKey": False }
      ],
      "foreignKeys": [
        { "column": "Pedido_idPedido", "referencesTable": "Pedido", "referencesColumn": "idPedido" },
        { "column": "Produto_idProduto", "referencesTable": "Produto", "referencesColumn": "idProduto" }
      ]
    }
  ]
}

