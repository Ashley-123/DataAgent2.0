import { BaseG2Chart } from '@/views/chat/component/BaseG2Chart.ts'
import type { ChartAxis, ChartData } from '@/views/chat/component/BaseChart.ts'
import type { G2Spec } from '@antv/g2'
import { checkIsPercent } from '@/views/chat/component/charts/utils.ts'

export class Line extends BaseG2Chart {
  //
  private seriesField: string | null = null
  private allLegendValues: string[] = []
  private originalData: any[] = []
  //
  constructor(id: string) {
    super(id, 'line')
  }

  init(axis: Array<ChartAxis>, data: Array<ChartData>) {
    super.init(axis, data)

    const x = this.axis.filter((item) => item.type === 'x')
    const y = this.axis.filter((item) => item.type === 'y')
    const series = this.axis.filter((item) => item.type === 'series')

    if (x.length == 0 || y.length == 0) {
      return
    }

    const _data = checkIsPercent(y[0], data)

    const options: G2Spec = {
      ...this.chart.options(),
      type: 'view',
      data: _data.data,
      encode: {
        x: x[0].value,
        y: y[0].value,
        color: series.length > 0 ? series[0].value : undefined,
      },
      axis: {
        x: {
          title: x[0].name,
          labelFontSize: 12,
          labelAutoHide: {
            type: 'hide',
            keepHeader: true,
            keepTail: true,
          },
          labelAutoRotate: false,
          labelAutoWrap: true,
          labelAutoEllipsis: true,
        },
        y: { title: y[0].name },
      },
      scale: {
        x: {
          nice: true,
        },
        y: {
          nice: true,
          type: 'linear',
        },
      },
      children: [
        {
          type: 'line',
          encode: {
            shape: 'smooth',
          },
          // labels: [
          //   {
          //     text: (data: any) => {
          //       const value = data[y[0].value]
          //       if (value === undefined || value === null) {
          //         return ''
          //       }
          //       return `${value}${_data.isPercent ? '%' : ''}`
          //     },
          //     style: {
          //       dx: -10,
          //       dy: -12,
          //     },
          //     transform: [
          //       { type: 'contrastReverse' },
          //       { type: 'exceedAdjust' },
          //       { type: 'overlapHide' },
          //     ],
          //   },
          // ],
          tooltip: (data) => {
            if (series.length > 0) {
              return {
                name: data[series[0].value],
                value: `${data[y[0].value]}${_data.isPercent ? '%' : ''}`,
              }
            } else {
              return { name: y[0].name, value: `${data[y[0].value]}${_data.isPercent ? '%' : ''}` }
            }
          },
        },
        {
          type: 'point',
          style: {
            fill: 'white',
          },
          encode: {
            size: 1.5,
          },
          tooltip: false,
        },
      ],
    } as G2Spec

    this.chart.options(options)

    //new lengend control function
    this.seriesField = series.length > 0 ? series[0].value : null
    this.originalData = [...data] // 深拷贝原始数据

    if (this.seriesField) {
      this.allLegendValues = [...new Set(data.map(d => d[this.seriesField!]))]
    }
  }
  
  toggleLegendItem(legendValue: string, visible: boolean) {
    if (!this.seriesField || !this.chart) return

    let filteredData

    if (visible) {
      filteredData = this.originalData
    } else {
      filteredData = this.originalData.filter((d: any) => d[this.seriesField!] !== legendValue)
    }

    this.chart.data(filteredData)
    this.chart.render()
  }

  //批量设置图例过滤
  setLegendFilter(hiddenItems: string[]) {
    if (!this.seriesField || !this.chart) return

    const filteredData = this.originalData.filter((d: any) => !hiddenItems.includes(d[this.seriesField!]))

    this.chart.data(filteredData)
    this.chart.render()
  }

  //设置要显示的图例项（只显示指定的项）
  showOnlyLegends(visibleItems: string[]) {
    if (!this.seriesField || !this.chart) return
    const filteredData = this.originalData.filter((d: any) => visibleItems.includes(d[this.seriesField!]))

    this.chart.data(filteredData)
    this.chart.render()
  }

//清除所有图例过滤，显示所有数据
  showAllLegends() {
    if (!this.chart) return

    this.chart.data(this.originalData)
    this.chart.render()
  }

  getAllLegendValues(): string[] {
    return this.allLegendValues
  }

  getSeriesField(): string | null {
    return this.seriesField
  }

  showLegendsByString(legendString: string) {
    if (typeof legendString !== 'string') {
      console.warn('⚠️ [Line Chart] legendString 不是字符串类型:', legendString)
      return
    }

    if (!legendString || legendString.trim().toLowerCase() === 'all') {
      this.showAllLegends()
      return
    }

    if (legendString.trim().toLowerCase() === 'none') {
      this.showOnlyLegends([])
      return
    }
// 支持中英文逗号、分号、换行
    const legendArray = legendString
      .split(/[,\n;，；]/)  
      .map(item => item.trim())  
      .filter(item => item.length > 0)  
      .filter(item => this.allLegendValues.includes(item))  // 只保留有效的图例值

    if (legendArray.length === 0) {
      ElMessage({
        message: "⚠️ invalid legend ",
        type: 'error',
        showClose: true,
      })
      console.log('invalid legend ')
      this.showAllLegends()
      return
    }

    // 显示指定的图例
    this.showOnlyLegends(legendArray)
  }

//通过逗号分隔的字符串批量隐藏图例
  hideLegendsByString(hiddenString: string) {
    if (!hiddenString || hiddenString.trim().toLowerCase() === 'none') {
      this.showAllLegends()
      return
    }

    if (hiddenString.trim().toLowerCase() === 'all') {
      this.showOnlyLegends([])
      return
    }

    const hiddenArray = hiddenString
      .split(/[,\n;，；]/)
      .map(item => item.trim())
      .filter(item => item.length > 0)
      .filter(item => this.allLegendValues.includes(item))

    // 设置隐藏过滤
    this.setLegendFilter(hiddenArray)
  }

  applyLegendControl(legendString: string) {
    this.showLegendsByString(legendString)
  }
}

