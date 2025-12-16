<script setup lang="ts">
  import 'highlight.js/styles/github.min.css'
  import 'github-markdown-css/github-markdown-light.css'
  import hljs from 'highlight.js'
  import { useI18n } from 'vue-i18n'
  import { ref, watch } from 'vue'
  
  const { t } = useI18n()
  const props = defineProps<{
    sql: string
    recordId?: number  
  }>()
  
  const emits = defineEmits<{
    'update:sql': [value: string]
    're-execute-sql': [params: { recordId: number; sql: string }]  
  }>()
  
  // 编辑状态
  const isEditing = ref(false)
  // 编辑中的 SQL 内容
  const editingSql = ref('')
  
  // 监听 props.sql 变化，同步到编辑内容
  watch(() => props.sql, (newVal) => {
    if (!isEditing.value) {
      editingSql.value = newVal
    }
  }, { immediate: true })
  
  // 切换到编辑模式
  const enterEditMode = () => {
    isEditing.value = true
    editingSql.value = props.sql
  }
  const saveEdit = () => {
    // 触发事件，将修改后的 SQL 传递给父组件
    emits('update:sql', editingSql.value)
    isEditing.value = false
  }
  
  // 重新执行 SQL
  const RefreashSQL = () => {
    // 如果提供了 recordId，触发重新执行事件
    if (props.recordId) {
      emits('re-execute-sql', {
        recordId: props.recordId,
        sql: editingSql.value
      })
      // 退出编辑模式
      isEditing.value = false
    } 
  }
  
  // 取消编辑
  const cancelEdit = () => {
    editingSql.value = props.sql
    isEditing.value = false
  }
    
  </script>
  <template>
    <div class="sql-component-container">
      <!-- 操作按钮区域 -->
      <div class="sql-actions">
        <div v-if="!isEditing">
        <button 
          class="btn-edit-sql" 
          @click="enterEditMode"
        >
          {{ t('chat.edit_sql') }}
        </button>
        <!-- 执行按钮 -->
        <button
        class="btn-edit-sql"
        @click="RefreashSQL"
        >{{ t('chat.execute_sql') }}
        </button>
      </div>
        <template v-else>
          <button class="btn-save-sql" @click="saveEdit">
            {{ t('chat.save_sql') }}
          </button>
          <button class="btn-cancel-sql" @click="cancelEdit">
            {{ t('chat.cancel_sql') }}
          </button>
         <!-- 效正，后续可以加一个 -->
          <!-- <button
          class="btn-edit-sql"
          @click="Correct"
          >{{ t('chat.show_sql') }}
          </button> -->
          
        </template>
      </div>
  
      <!-- SQL 显示/编辑区域 -->
      <div v-if="!isEditing" class="sql-display">
        <pre class="hljs">
          <div
            v-dompurify-html="hljs.highlight(props.sql, { language: 'sql', ignoreIllegals: true }).value"
          ></div>
        </pre>
      </div>
      <div v-else class="sql-edit">
        <textarea
          v-model="editingSql"
          class="sql-textarea"
        ></textarea>
      </div>
    </div>
  </template>
  
  <style lang="less">
  .sql-component-container {
    position: relative;
  }
  
  .sql-actions {
    display: flex;
    gap: 8px;
    margin-bottom: 8px;
  }
  
  .btn-edit-sql,
  .btn-save-sql,
  .btn-cancel-sql {
    padding: 6px 12px;
    border: 1px solid rgb(227, 222, 222);
    border-radius: 4px;
    background: rgba(245, 246, 247, 1);
    cursor: pointer;
    font-size: 14px;
    transition: all 0.2s;
    margin-right: 20px;
  
    &:hover {
      background: rgba(235, 236, 237, 1);
      border-color: var(--ed-color-primary);
    }
  
    &:active {
      background: rgba(225, 226, 227, 1);
    }
  }
  
  .btn-save-sql {
    background: var(--ed-color-primary);
    color: white;
    border-color: var(--ed-color-primary);
  
    &:hover {
      background: var(--ed-color-primary-dark-2);
      border-color: var(--ed-color-primary-dark-2);
    }
  }
  
  .btn-cancel-sql {
    &:hover {
      border-color: rgba(222, 224, 227, 1);
    }
  }
  
  .sql-display {
    .hljs {
      margin-top: 0;
      overflow: auto;
      padding: 1rem;
      display: block;
  
      background: rgba(245, 246, 247, 1);
      border: 1px solid rgba(222, 224, 227, 1);
      border-radius: 6px;
    }
  }
  
  .sql-edit {
    .sql-textarea {
      width: 100%;
      min-height: 200px;
      padding: 1rem;
      font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'source-code-pro', monospace;
      font-size: 14px;
      line-height: 1.6;
      border: 1px solid rgba(222, 224, 227, 1);
      border-radius: 6px;
      background: rgba(255, 255, 255, 1);
      resize: vertical;
      outline: none;
      transition: border-color 0.2s;
  
      &:focus {
        border-color: var(--ed-color-primary);
        box-shadow: 0 0 0 2px rgba(var(--ed-color-primary-rgb), 0.1);
      }
  
      &::placeholder {
        color: rgba(143, 149, 158, 1);
      }
    }
  }
  </style>
  