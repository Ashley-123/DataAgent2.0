import { request } from '@/utils/request'

export const promptApi = {
  getList: (pageNum: any, pageSize: any, type: any) =>
    request.get(`/system/template-prompt/page/${pageNum}/${pageSize}?type=${type}`),

  addandputPrompt:(data: any)=>request.put(`/system/template-prompt`, data),

  deletePrompt:(data: any)=>{
    return request.delete(`/system/template-prompt`, { data: data })
  },

  UsePrompt:(id:number,TF:Boolean)=>{
    return request.get(`/system/template-prompt/${id}/enable/${TF}`)
  },
  
  acquirePromptbyId:(id:number)=>{
    return request.get(`/system/template-prompt/${id}`)
  },




  // getList: (pageNum: any, pageSize: any, type: any, params: any) =>
  //   request.get(`/system/custom_prompt/${type}/page/${pageNum}/${pageSize}${params}`),
  updateEmbedded: (data: any) => request.put(`/system/custom_prompt`, data),
  deleteEmbedded: (params: any) => request.delete('/system/custom_prompt', { data: params }),
  getOne: (id: any) => request.get(`/system/custom_prompt/${id}`),
  export2Excel: (type: any, params: any) =>
    request.get(`/system/custom_prompt/${type}/export`, {
      params,
      responseType: 'blob',
      requestOptions: { customError: true },
    }),
}
