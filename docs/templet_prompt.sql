--用户提示词表
-- 功能：存储可复用的提示词模板，用于关联数据源生成特定查询或指令。
CREATE TABLE template_prompt (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    oid BIGINT NOT NULL COMMENT '组织ID',
    type VARCHAR(50) NOT NULL COMMENT '提示词类型',
    name VARCHAR(255) NOT NULL COMMENT '提示词名称',
    content TEXT NOT NULL COMMENT '提示词内容',
    datasource_id BIGINT COMMENT '关联的数据源ID',
    enabled BOOLEAN DEFAULT true COMMENT '是否启用',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COMMENT='模板提示词表';