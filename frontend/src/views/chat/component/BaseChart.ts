export interface ChartAxis {
  name: string
  value: string
  type?: 'x' | 'y' | 'series'
}

export interface ChartData {
  [key: string]: any
}

export type ChartTypes = 'table' | 'bar' | 'column' | 'line' | 'pie' | 'scatter' | 'spec'

export abstract class BaseChart {
  id: string
  _name: string = 'base-chart'
  axis: Array<ChartAxis> = []
  data: Array<ChartData> = []
  // Optional options bag for advanced/spec rendering
  options: any

  constructor(id: string, name: string) {
    this.id = id
    this._name = name
  }

  init(axis: Array<ChartAxis>, data: Array<ChartData>): void {
    this.axis = axis
    this.data = data
  }

  // For advanced/spec charts; default no-op
  setOptions(options: any): void {
    this.options = options
  }

  abstract render(): void

  abstract destroy(): void
}
