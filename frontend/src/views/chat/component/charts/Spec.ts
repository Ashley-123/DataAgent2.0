import { BaseG2Chart } from '@/views/chat/component/BaseG2Chart'
import type { ChartAxis, ChartData } from '@/views/chat/component/BaseChart'

export class Spec extends BaseG2Chart {
  constructor(id: string) {
    super(id, 'spec')
  }

  init(axis: Array<ChartAxis>, data: Array<ChartData>) {
    // Keep compatibility with base init for future reuse if needed
    super.init(axis, data)
  }

  render() {
    // Expect full G2 options stored in this.options; pass through directly
    const options = (this.options || {}) as unknown
    // Bypass strict typing to allow any valid G2 spec tree
    this.chart.options(options as any)
    super.render()
  }
}


