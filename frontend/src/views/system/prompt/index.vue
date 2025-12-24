<script lang="ts" setup>
import { nextTick, onMounted, reactive, ref, unref } from 'vue'
import icon_export_outlined from '@/assets/svg/icon_export_outlined.svg'
import { promptApi } from '@/api/prompt'
import { formatTimestamp } from '@/utils/date'
import { datasourceApi } from '@/api/datasource'
import icon_add_outlined from '@/assets/svg/icon_add_outlined.svg'
import IconOpeEdit from '@/assets/svg/icon_edit_outlined.svg'
import icon_copy_outlined from '@/assets/embedded/icon_copy_outlined.svg'
import IconOpeDelete from '@/assets/svg/icon_delete.svg'
import icon_searchOutline_outlined from '@/assets/svg/icon_search-outline_outlined.svg'
import EmptyBackground from '@/views/dashboard/common/EmptyBackground.vue'
import { useClipboard } from '@vueuse/core'
import { useI18n } from 'vue-i18n'
import { cloneDeep } from 'lodash-es'
import { convertFilterText, FilterText } from '@/components/filter-text'
import { DrawerMain } from '@/components/drawer-main'
import iconFilter from '@/assets/svg/icon-filter_outlined.svg'
import Uploader from '@/views/system/excel-upload/Uploader.vue'

interface Form {
  id?: string | null
  type: string | null
  prompt: string | null
  specific_ds: boolean
  datasource_ids: number[]
  datasource_names: string[]
  name: string | null
}

const drawerMainRef = ref() 
const { t } = useI18n() 
const { copy } = useClipboard({ legacy: true }) 
const multipleSelectionAll = ref<any[]>([]) 
const keywords = ref('') 
const oldKeywords = ref('')
const searchLoading = ref(false) 
const currentType = ref('chart') 

const options = ref<any[]>([]) 
const selectable = () => {
  return true
}


const state = reactive<any>({
  conditions: [], 
  filterTexts: [], 
})

onMounted(() => {
  datasourceApi.list().then((res) => {
    filterOption.value[0].option = [...res]
    options.value = [...res]
  })
  search()
})

const dialogFormVisible = ref<boolean>(false) 
const multipleTableRef = ref() 
const isIndeterminate = ref(true) 
const checkAll = ref(false) 
const fieldList = ref<any>([])
const pageInfo = reactive({
  currentPage: 1, 
  pageSize: 10, 
  total: 0, 
})

const dialogTitle = ref('') 
const updateLoading = ref(false)
const defaultForm = {
  id: null,
  type: null,
  prompt: null,
  datasource_ids: [],
  datasource_names: [],
  name: null,
  specific_ds: false,
}
const pageForm = ref<Form>(cloneDeep(defaultForm))

const copyCode = () => {
  copy(pageForm.value.prompt!)
    .then(function () {
      ElMessage.success(t('embedded.copy_successful'))
    })
    .catch(function () {
      ElMessage.error(t('embedded.copy_failed'))
    })
}

const cancelDelete = () => {
  handleToggleRowSelection(false)
  multipleSelectionAll.value = []
  checkAll.value = false
  isIndeterminate.value = false
}

const getFileName = () => {
  let title = ''
  if (currentType.value === 'GENERATE_SQL') {
    title = t('prompt.ask_sql')
  }
  if (currentType.value === 'ANALYSIS') {
    title = t('prompt.data_analysis')
  }
  if (currentType.value === 'PREDICT_DATA') {
    title = t('prompt.data_prediction')
  }
  return `${title}.xlsx`
}

const exportExcel = () => {
  let title = ''
  if (currentType.value === 'GENERATE_SQL') {
    title = t('prompt.ask_sql')
  }
  if (currentType.value === 'ANALYSIS') {
    title = t('prompt.data_analysis')
  }
  if (currentType.value === 'PREDICT_DATA') {
    title = t('prompt.data_prediction')
  }
  // 显示确认对话框，提示用户将导出多少条记录
  ElMessageBox.confirm(t('prompt.export_hint', { msg: pageInfo.total, type: title }), {
    confirmButtonType: 'primary',
    confirmButtonText: t('professional.export'),
    cancelButtonText: t('common.cancel'),
    customClass: 'confirm-no_icon',
    autofocus: false,
  }).then(() => {
    searchLoading.value = true
    // 调用导出 API，如果有搜索关键词则传递关键词参数
    promptApi
      .export2Excel(currentType.value, keywords.value ? { name: keywords.value } : {})
      .then((res) => {
        // 创建 Excel 文件的 Blob 对象
        const blob = new Blob([res], {
          type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })
        // 创建下载链接并触发下载
        const link = document.createElement('a')
        link.href = URL.createObjectURL(blob)
        link.download = `${title}.xlsx`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      })
      .catch(async (error) => {
        if (error.response) {
          try {
            let text = await error.response.data.text()
            try {
              text = JSON.parse(text)
            } finally {
              ElMessage({
                message: text,
                type: 'error',
                showClose: true,
              })
            }
          } catch (e) {
            console.error('Error processing error response:', e)
          }
        } else {
          console.error('Other error:', error)
          ElMessage({
            message: error,
            type: 'error',
            showClose: true,
          })
        }
      })
      .finally(() => {
        searchLoading.value = false
      })
  })
}

const deleteBatchUser = () => {
  ElMessageBox.confirm(
    t('prompt.selected_prompt_words', { msg: multipleSelectionAll.value.length }),
    {
      confirmButtonType: 'danger',
      confirmButtonText: t('dashboard.delete'),
      cancelButtonText: t('common.cancel'),
      customClass: 'confirm-no_icon',
      autofocus: false,
    }
  ).then(() => {
    // 提取所有选中项的 ID 并调用删除 API
    promptApi.deletePrompt(multipleSelectionAll.value.map((ele) => ele.id)).then(() => {
      ElMessage({
        type: 'success',
        message: t('dashboard.delete_success'),
      })
      multipleSelectionAll.value = []
      search()
    })
  })
}

const deleteHandler = (row: any) => {
  ElMessageBox.confirm(t('prompt.prompt_word_name_de', { msg: row.name }), {
    confirmButtonType: 'danger',
    confirmButtonText: t('dashboard.delete'),
    cancelButtonText: t('common.cancel'),
    customClass: 'confirm-no_icon',
    autofocus: false,
  }).then(() => {
    promptApi.deletePrompt([row.id]).then(() => {
      // 从跨页选中列表中移除该项
      multipleSelectionAll.value = multipleSelectionAll.value.filter((ele) => row.id !== ele.id)
      ElMessage({
        type: 'success',
        message: t('dashboard.delete_success'),
      })
      search()
    })
  })
}
const toggleEnabled = (row: any) => {
  const newStatus = row.enabled ? t('prompt.enabled') : t('prompt.disabled')
  promptApi.addandputPrompt({
    ...row,
    enabled: row.enabled
  }).then(() => {
    ElMessage({
      type: 'success',
      message: t('prompt.prompt_word_name_success', { msg: newStatus }),
    })
  }).catch(() => {
    row.enabled = !row.enabled
    ElMessage({
      type: 'error',
      message: t('prompt.prompt_word_name_failed', { msg: newStatus }),
    })
  })
}

const handleSelectionChange = (val: any[]) => {
  if (toggleRowLoading.value) return 
  const arr = fieldList.value.filter(selectable) 
  const ids = arr.map((ele: any) => ele.id) 

  multipleSelectionAll.value = [
    ...multipleSelectionAll.value.filter((ele: any) => !ids.includes(ele.id)),
    ...val,
  ]

  isIndeterminate.value = !(val.length === 0 || val.length === arr.length)
  checkAll.value = val.length === arr.length
}

const handleCheckAllChange = (val: any) => {
  isIndeterminate.value = false 
  handleSelectionChange(val ? fieldList.value.filter(selectable) : [])
  if (val) {
    handleToggleRowSelection()
  } else {
    multipleTableRef.value.clearSelection()
  }
}

const toggleRowLoading = ref(false) 

const handleToggleRowSelection = (check: boolean = true) => {
  toggleRowLoading.value = true
  const arr = fieldList.value.filter(selectable) // 当前页所有可选行
  let i = 0 
  const ids = multipleSelectionAll.value.map((ele: any) => ele.id) // 跨页选中列表的所有 ID
  for (const key in arr) {
    if (ids.includes((arr[key] as any).id)) {
      i += 1
      multipleTableRef.value.toggleRowSelection(arr[key], check)
    }
  }
  toggleRowLoading.value = false
  // 更新全选复选框状态
  checkAll.value = i === arr.length 
  isIndeterminate.value = !(i === 0 || i === arr.length) 
}


const search = () => {
  searchLoading.value = true
  oldKeywords.value = keywords.value
  promptApi
    .getList(pageInfo.currentPage, pageInfo.pageSize, currentType.value)
    .then((res: any) => {
      toggleRowLoading.value = true
      // 数据映射：将 content 字段映射为 prompt
      fieldList.value = res.data.map((item: any) => {
        const datasource_names = item.datasource_id
          ? (() => {
            const matchedOption = options.value.find((opt: any) => opt.id === item.datasource_id)
            return matchedOption ? [matchedOption.name] : [`数据源${item.datasource_id}`]
          })()
          : []

        return {
          ...item,
          prompt: item.content, 
          specific_ds: item.datasource_id ? true : false, 
          datasource_names, 
        }
      })
      pageInfo.total = res.total_count 
      searchLoading.value = false
      nextTick(() => {
        handleToggleRowSelection()
      })
    })
    .finally(() => {
      searchLoading.value = false
    })
}

const termFormRef = ref() 


const validatePass = (_: any, value: any, callback: any) => {
  if (pageForm.value.specific_ds && !value.length) {
    callback(new Error(t('datasource.Please_select') + t('common.empty') + t('ds.title')))
  } else {
    callback()
  }
}


const rules = {
  name: [
    {
      required: true, 
      message: t('datasource.please_enter') + t('common.empty') + t('prompt.prompt_word_name'),
    },
  ],
  datasource_ids: [
    {
      validator: validatePass, 
      trigger: 'blur',
    },
  ],
  prompt: [
    {
      required: true,
      message: t('datasource.please_enter') + t('common.empty') + t('prompt.replaced_with'),
    },
  ],
}


const list = () => {
  datasourceApi.list().then((res: any) => {
    options.value = res || []
  })
}

/**
 * saveHandler 函数
 */
// const saveHandler = () => {
//   termFormRef.value.validate((res: any) => {
//     if (res) {
//       // res 为 true 表示验证通过（Element Plus 的 validate 回调逻辑）
//       const obj = unref(pageForm)
//       if (!obj.id) {
//         delete obj.id // 新增时删除 id 字段
//       }
//       updateLoading.value = true
//       promptApi
//         .updateEmbedded(obj)
//         .then(() => {
//           ElMessage({
//             type: 'success',
//             message: t('common.save_success'),
//           })
//           search() // 刷新列表
//           onFormClose() // 关闭抽屉
//         })
//         .finally(() => {
//           updateLoading.value = false
//         })
//     }
//   })
// }
//新保存接口
const saveHandler = () => {
  termFormRef.value.validate((res: any) => {
    if (res) {
      const obj = unref(pageForm)
      if (!obj.id) {
        delete obj.id 
      }
      updateLoading.value = true
      
      
      const data = {
        "type": obj.type || '',
        "name": obj.name || '',
        "content": obj.prompt || '',
        "datasource_id": obj.datasource_ids.length > 0 ? obj.datasource_ids.join(',') : null,
        "enabled": true,
      }
      promptApi
        .addandputPrompt(data)
        .then(() => {
          ElMessage({
            type: 'success',
            message: t('common.save_success'),
          })
          search() 
          onFormClose() 
        })
        .finally(() => {
          updateLoading.value = false
        })
    }
  })
}

const editHandler = (row: any) => {
  pageForm.value.id = null
  pageForm.value.type = unref(currentType) 
  if (row) {
    pageForm.value = cloneDeep(row) 
  }
  list()
  dialogTitle.value = row?.id ? t('prompt.edit_prompt_word') : t('prompt.add_prompt_word')
  dialogFormVisible.value = true

}

const onFormClose = () => {
  pageForm.value = cloneDeep(defaultForm)
  dialogFormVisible.value = false
}


const handleSizeChange = (val: number) => {
  pageInfo.currentPage = 1
  pageInfo.pageSize = val
  search()
}

const handleCurrentChange = (val: number) => {
  pageInfo.currentPage = val
  search()
}

const rowInfoDialog = ref(false) 


const handleRowClick = (row: any) => {
  pageForm.value = cloneDeep(row)
  rowInfoDialog.value = true
}


const onRowFormClose = () => {
  pageForm.value = cloneDeep(defaultForm)
  rowInfoDialog.value = false
}


const handleChange = () => {
  termFormRef.value.validateField('datasource_ids')
}

const typeChange = (val: any) => {
  currentType.value = val
  pageInfo.currentPage = 1
  search()
}


const filterOption = ref<any[]>([
  {
    type: 'select', 
    option: [], 
    field: 'dslist', 
    title: t('ds.title'), 
    operate: 'in', 
    property: { placeholder: t('common.empty') + t('ds.title') }, 
  },
])

const fillFilterText = () => {
  const textArray = state.conditions?.length
    ? convertFilterText(state.conditions, filterOption.value)
    : []
  state.filterTexts = [...textArray]
  Object.assign(state.filterTexts, textArray)
}


const searchCondition = (conditions: any) => {
  state.conditions = conditions
  fillFilterText()
  search()
  drawerMainClose()
}

const clearFilter = (params?: number) => {
  let index = params ? params : 0
  if (isNaN(index)) {
    state.filterTexts = []
  } else {
    state.filterTexts.splice(index, 1)
  }
  drawerMainRef.value.clearFilter(index)
}

const drawerMainOpen = async () => {
  drawerMainRef.value.init()
}

const drawerMainClose = () => {
  drawerMainRef.value.close()
}
</script>

<template>
  <div class="prompt">
    <div class="tool-left">
      <div class="btn-select">
        <!-- 生成SQL类型按钮 -->
        <!-- <el-button
            :class="[currentType === 'sql' && 'is-active']"
            text
            @click="typeChange('sql')"
          >
            {{ $t('prompt.ask_sql') }}真 sql提示词
          </el-button> -->
        <el-button :class="[currentType === 'chart' && 'is-active']" text @click="typeChange('chart')">
          {{ $t('prompt.data_chart') }}
        </el-button>
        <el-button :class="[currentType === 'analysis' && 'is-active']" text @click="typeChange('analysis')">
          {{ $t('prompt.data_analysis') }}
        </el-button>
        <el-button :class="[currentType === 'predict' && 'is-active']" text @click="typeChange('predict')">
          {{ $t('prompt.data_prediction') }}
        </el-button>


      </div>
      <div class="tool-row">
        <el-input v-model="keywords" style="width: 240px; margin-right: 12px" :placeholder="$t('dashboard.search')"
          clearable @blur="search">
          <template #prefix>
            <el-icon>
              <icon_searchOutline_outlined />
            </el-icon>
          </template>
        </el-input>
        <!-- 导出Excel按钮 -->
        <el-button secondary @click="exportExcel">
          <template #icon>
            <icon_export_outlined />
          </template>
          {{ $t('professional.export_all') }}
        </el-button>
        <Uploader :upload-path="`/system/custom_prompt/${currentType}/uploadExcel`"
          :template-path="`/system/custom_prompt/template`" :template-name="getFileName()" @upload-finished="search" />
        <el-button class="no-margin" secondary @click="drawerMainOpen">
          <template #icon>
            <iconFilter></iconFilter>
          </template>
          {{ $t('user.filter') }}
        </el-button>
        <el-button class="no-margin" type="primary" @click="editHandler(null)">
          <template #icon>
            <icon_add_outlined></icon_add_outlined>
          </template>
          {{ $t('prompt.add_prompt_word') }}
        </el-button>
      </div>
    </div>
    <div v-if="!searchLoading" class="table-content" :class="multipleSelectionAll?.length && 'show-pagination_height'">
      <filter-text :total="pageInfo.total" :filter-texts="state.filterTexts" @clear-filter="clearFilter" />
      <div class="preview-or-schema">
        <el-table ref="multipleTableRef" :data="fieldList" style="width: 100%" @row-click="handleRowClick"
          @selection-change="handleSelectionChange">
          <el-table-column :selectable="selectable" type="selection" width="55" />
          <el-table-column prop="name" :label="$t('prompt.prompt_word_name')" width="280">
          </el-table-column>
          <el-table-column prop="prompt" :label="$t('prompt.prompt_word_content')" min-width="240">
            <template #default="scope">
              <div class="field-comment_d">
                <span :title="scope.row.prompt" class="notes-in_table">{{ scope.row.prompt }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column :label="$t('training.effective_data_sources')" min-width="240"><template #default="scope">
              <div v-if="scope.row.specific_ds" class="field-comment_d">
                <span :title="scope.row.datasource_names" class="notes-in_table">{{
                  scope.row.datasource_names.join(',')
                }}</span>
              </div>
              <div v-else>{{ t('training.all_data_sources') }}</div>
            </template>
          </el-table-column>
          <el-table-column prop="create_time" sortable :label="$t('dashboard.create_time')" width="240">
            <template #default="scope">
              <span>{{ formatTimestamp(scope.row.create_time, 'YYYY-MM-DD HH:mm:ss') }}</span>
            </template>
          </el-table-column>
          <el-table-column fixed="right" width="160" :label="t('ds.actions')">
            <template #default="scope">
              <div class="field-comment">
                <el-tooltip :offset="14" effect="dark" :content="$t('datasource.edit')" placement="top">
                  <el-icon class="action-btn" size="16" @click.stop="editHandler(scope.row)">
                    <IconOpeEdit></IconOpeEdit>
                  </el-icon>
                </el-tooltip>
                <!-- 刪除列，加一个操作启动列 -->
                <el-tooltip :offset="14" effect="dark" :content="$t('dashboard.delete')" placement="top">
                  <el-icon class="action-btn" size="16" @click.stop="deleteHandler(scope.row)">
                    <IconOpeDelete></IconOpeDelete>
                  </el-icon>
                </el-tooltip>
                <!--  启用/禁用文本 -->
                <el-tooltip :offset="14" effect="dark" :content="scope.row.enabled ? $t('prompt.enabled') : $t('prompt.disabled')" placement="top">
                <el-switch
                  v-model="scope.row.enabled"
                  @click.stop="toggleEnabled(scope.row)"
                  size="small"
                >
                </el-switch>
              </el-tooltip>
              </div>
            </template>
          </el-table-column>
          <template #empty>
            <EmptyBackground v-if="!!oldKeywords && !fieldList.length"
              :description="$t('datasource.relevant_content_found')" img-type="tree" />
            <template v-if="!oldKeywords && !fieldList.length">
              <EmptyBackground class="datasource-yet" :description="$t('prompt.no_prompt_words')"
                img-type="noneWhite" />

              <div style="text-align: center; margin-top: -23px">
                <el-button type="primary" @click="editHandler(null)">
                  <template #icon>
                    <icon_add_outlined></icon_add_outlined>
                  </template>
                  {{ $t('prompt.add_prompt_word') }}
                </el-button>
              </div>
            </template>
          </template>
        </el-table>
      </div>
    </div>

    <div v-if="fieldList.length" class="pagination-container">
      <el-pagination v-model:current-page="pageInfo.currentPage" v-model:page-size="pageInfo.pageSize"
        :page-sizes="[10, 20, 30]" :background="true" layout="total, sizes, prev, pager, next, jumper"
        :total="pageInfo.total" @size-change="handleSizeChange" @current-change="handleCurrentChange" />
    </div>
    <div v-if="multipleSelectionAll.length" class="bottom-select">
      <el-checkbox v-model="checkAll" :indeterminate="isIndeterminate" @change="handleCheckAllChange">
        {{ $t('datasource.select_all') }}
      </el-checkbox>

      <button class="danger-button" @click="deleteBatchUser">{{ $t('dashboard.delete') }}</button>

      <span class="selected">{{
        $t('user.selected_2_items', { msg: multipleSelectionAll.length })
      }}</span>

      <el-button text @click="cancelDelete">
        {{ $t('common.cancel') }}
      </el-button>
    </div>
  </div>

  <el-drawer v-model="dialogFormVisible" :title="dialogTitle" destroy-on-close size="600px" :before-close="onFormClose"
    modal-class="prompt-add_drawer">
    <el-form ref="termFormRef" :model="pageForm" label-width="180px" label-position="top" :rules="rules"
      class="form-content_error" @submit.prevent>
      <el-form-item prop="name" :label="t('prompt.prompt_word_name')">
        <el-input v-model="pageForm.name" :placeholder="$t('datasource.please_enter') + $t('common.empty') + $t('prompt.prompt_word_name')
          " autocomplete="off" maxlength="50" clearable />
      </el-form-item>
      <el-form-item prop="prompt" :label="t('prompt.prompt_word_content')">
        <el-input v-model="pageForm.prompt" :placeholder="$t('prompt.replaced_with')"
          :autosize="{ minRows: 3.636, maxRows: 11.09 }" type="textarea" />
        <div class="tips">
          {{ t('prompt.loss_exercise_caution') }}
        </div>
      </el-form-item>

      <el-form-item class="is-required" :class="!pageForm.specific_ds && 'no-error'" prop="datasource_ids"
        :label="t('training.effective_data_sources')">
        <el-radio-group v-model="pageForm.specific_ds">
          <el-radio :value="false">{{ $t('training.all_data_sources') }}</el-radio>
          <el-radio :value="true">{{ $t('training.partial_data_sources') }}</el-radio>
        </el-radio-group>
        <el-select v-if="pageForm.specific_ds" v-model="pageForm.datasource_ids" multiple filterable
          :placeholder="$t('datasource.Please_select') + $t('common.empty') + $t('ds.title')"
          style="width: 100%; margin-top: 8px" @change="handleChange">
          <el-option v-for="item in options" :key="item.id" :label="item.name" :value="item.id" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <div v-loading="updateLoading" class="dialog-footer">
        <el-button secondary @click="onFormClose">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="saveHandler">
          {{ $t('common.save') }}
        </el-button>
      </div>
    </template>
  </el-drawer>
  <el-drawer v-model="rowInfoDialog" :title="$t('menu.Details')" destroy-on-close size="600px"
    :before-close="onRowFormClose" modal-class="prompt-term_drawer">
    <el-form label-width="180px" label-position="top" class="form-content_error" @submit.prevent>
      <el-form-item :label="t('prompt.prompt_word_name')">
        <div class="content">
          {{ pageForm.name }}
        </div>
      </el-form-item>
      <el-form-item :label="t('prompt.prompt_word_content')">
        <div style="white-space: pre-wrap" class="content">
          {{ pageForm.prompt }}
        </div>
        <div class="copy-icon">
          <el-tooltip :offset="12" effect="dark" :content="t('datasource.copy')" placement="top">
            <el-icon class="hover-icon_with_bg" style="cursor: pointer" size="16" @click="copyCode">
              <icon_copy_outlined></icon_copy_outlined>
            </el-icon>
          </el-tooltip>
        </div>
      </el-form-item>
      <el-form-item :label="t('ds.title')">
        <div class="content">
          {{
            pageForm.datasource_names.length && pageForm.specific_ds
              ? pageForm.datasource_names.join()
              : t('training.all_data_sources')
          }}
        </div>
      </el-form-item>
    </el-form>
  </el-drawer>
  <drawer-main ref="drawerMainRef" :filter-options="filterOption" @trigger-filter="searchCondition" />
</template>

<style lang="less" scoped>
.no-margin {
  margin: 0;
}

.prompt {
  height: 100%;
  position: relative;

  .datasource-yet {
    padding-bottom: 0;
    height: auto;
    padding-top: 160px;
  }

  :deep(.ed-table__cell) {
    cursor: pointer;
  }

  .tool-row {
    display: flex;
    align-items: center;
    flex-direction: row;
    gap: 8px;
  }

  .tool-left {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;

    .btn-select {
      height: 32px;
      display: inline-flex;
      padding: 0 4px;
      align-items: center;
      justify-content: center;
      background: #ffffff;
      border: 1px solid var(--ed-border-color);
      border-radius: 6px;

      .is-active {
        background: var(--ed-color-primary-1a, #1cba901a);
        font-weight: 500;
      }

      .ed-button:not(.is-active) {
        color: #1f2329;
      }

      .ed-button.is-text {
        height: 24px;
        padding: 0 8px;
        line-height: 22px;
      }

      .ed-button+.ed-button {
        margin-left: 4px;
      }
    }
  }

  .pagination-container {
    display: flex;
    justify-content: end;
    align-items: center;
    margin-top: 16px;
  }

  .table-content {
    max-height: calc(100% - 104px);
    overflow-y: auto;

    &.show-pagination_height {
      max-height: calc(100% - 165px);
    }

    .preview-or-schema {
      .field-comment_d {
        display: flex;
        align-items: center;
        min-height: 24px;
      }

      .notes-in_table {
        max-width: 100%;
        display: -webkit-box;
        max-height: 44px;
        -webkit-box-orient: vertical;
        -webkit-line-clamp: 2;
        /* 限制行数为3 */
        overflow: hidden;
        text-overflow: ellipsis;
        word-break: break-word;
        white-space: pre-wrap;
      }

      .ed-icon {
        color: #646a73;
      }

      .user-status-container {
        display: flex;
        align-items: center;
        font-weight: 400;
        font-size: 14px;
        line-height: 22px;
        height: 24px;

        .ed-icon {
          margin-left: 8px;
        }
      }

      .field-comment {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        gap: 8px;
        min-height: 32px;

        .ed-icon {
          position: relative;
          cursor: pointer;

          &::after {
            content: '';
            background-color: #1f23291a;
            position: absolute;
            border-radius: 6px;
            width: 24px;
            height: 24px;
            transform: translate(-50%, -50%);
            top: 50%;
            left: 50%;
            display: none;
          }

          &:not(.not-allow):hover {
            &::after {
              display: block;
            }
          }

          &.not-allow {
            cursor: not-allowed;
          }
        }
      }

      .preview-num {
        margin: 12px 0;
        font-weight: 400;
        font-size: 14px;
        line-height: 22px;
        color: #646a73;
      }
    }
  }

  .bottom-select {
    position: absolute;
    height: 64px;
    width: calc(100% + 48px);
    left: -24px;
    bottom: -16px;
    border-top: 1px solid #1f232926;
    display: flex;
    background-color: #fff;
    align-items: center;
    padding-left: 24px;
    background-color: #fff;
    z-index: 10;

    .danger-button {
      border: 1px solid var(--ed-color-danger);
      color: var(--ed-color-danger);
      border-radius: var(--ed-border-radius-base);
      min-width: 80px;
      height: 32px;
      line-height: 32px;
      text-align: center;
      cursor: pointer;
      margin: 0 16px;
      background-color: transparent;
    }

    .primary-button {
      border: 1px solid var(--ed-color-primary);
      color: var(--ed-color-primary);
      border-radius: var(--ed-border-radius-base);
      min-width: 80px;
      height: 32px;
      line-height: 32px;
      text-align: center;
      cursor: pointer;
      margin: 0 16px;
      background-color: transparent;
    }

    .selected {
      font-weight: 400;
      font-size: 14px;
      line-height: 22px;
      color: #646a73;
      margin-right: 12px;
    }
  }
}
</style>
<style lang="less">
.prompt-term_drawer {
  .ed-form-item--label-top .ed-form-item__label {
    margin-bottom: 4px;
  }

  .ed-form-item__label {
    color: #646a73;
  }

  .content {
    width: 100%;
    line-height: 22px;
    word-break: break-all;
  }

  .copy-icon {
    position: absolute;
    right: 0;
    top: -27px;
  }
}

.prompt-add_drawer {
  .tips {
    font-weight: 400;
    font-size: 14px;
    line-height: 22px;
    color: #ff8800;
  }

  .no-error.no-error {
    .ed-form-item__error {
      display: none;
    }

    margin-bottom: 16px;
  }

  .ed-textarea__inner {
    line-height: 22px;
  }
}
</style>