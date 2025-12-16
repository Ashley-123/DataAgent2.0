import { BaseG2Chart } from '@/views/chat/component/BaseG2Chart.ts'
import type { ChartAxis, ChartData } from '@/views/chat/component/BaseChart.ts'
import type { G2Spec } from '@antv/g2'

export class Spec extends BaseG2Chart {
  constructor(id: string) {
    super(id, 'spec')
  }

  init(axis: Array<ChartAxis>, data: Array<ChartData>) {
    // Keep compatibility with base init for future reuse if needed
    super.init(axis, data)
  }

  render() {
    // Expect full G2 options stored in this.options
    const options = (this.options || {}) as G2Spec
    // Merge base chart defaults with provided options, user options take precedence
    const merged: G2Spec = {
      ...this.chart.options(),
      ...options,
    }
    this.chart.options(merged)
    super.render()
  }
}


