# Makefile for Aerich and Tortoise ORM management

# 告诉 Make 这些目标不是实际文件名
.PHONY: help init init-db migrate upgrade downgrade reset aerich

# 帮助文档，执行make不带参数
.DEFAULT: help

# 设置默认的配置路径和迁移目录
CONFIG_PATH = cores.model.TORTOISE_ORM
MIGRATIONS_DIR = ./migrations

# 显示帮助信息
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  init            初始化 Aerich"
	@echo "  init-db         初始化迁移目录并同步数据库"
	@echo "  migrate         生成新的迁移文件，必须提供迁移名称"
	@echo "  upgrade         应用所有未应用的迁移"
	@echo "  downgrade       回滚最后一个迁移"
	@echo "  reset           清除数据库和迁移记录"
	@echo "  help            显示帮助信息"


# 初始化 Aerich
init:
	@aerich init -t $(CONFIG_PATH)

# 初始化迁移目录并同步数据库
init-db:
	@aerich init-db

# 生成新的迁移文件，必须提供迁移名称
migrate:
	aerich migrate

# 应用所有未应用的迁移
upgrade:
	@aerich upgrade

# 回滚最后一个迁移
downgrade:
	@aerich downgrade

# 清除数据库和迁移记录
reset:
	@aerich downgrade
	@rm -rf $(MIGRATIONS_DIR)
