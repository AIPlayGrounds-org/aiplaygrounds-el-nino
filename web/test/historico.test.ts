import { describe, expect, it } from 'vitest'
import { loadDataset } from '../server/utils/loadDataset'
import {
  alignHistoryEvent,
  CURRENT_EVENT_ID,
  historyEventSelectorData,
  alignHistoryOniEvent,
  peakOfHistoryEvent,
  peakOfHistoryOniEvent,
  shapeHistoricoDataset,
  shapeHistoricoOniDataset,
} from '~/utils/historico'

describe('historical ERSST comparison', () => {
  it('aligns each event from its own onset month', async () => {
    const dataset = await loadDataset('noaa-ersst')

    expect(alignHistoryEvent(dataset.records, '1982-83', 'nino34')[0]).toEqual({
      offset: 1,
      month: '1982-07',
      value: 0.51,
    })
    expect(alignHistoryEvent(dataset.records, '1997-98', 'nino34')[0]?.month).toBe('1997-04')
    expect(alignHistoryEvent(dataset.records, '2017', 'nino12').at(-1)?.month).toBe('2017-04')
  })

  it('computes the peak value and month for the selected region', async () => {
    const dataset = await loadDataset('noaa-ersst')

    expect(peakOfHistoryEvent(dataset.records, '1982-83', 'nino34')).toMatchObject({
      value: 2.29,
      month: '1983-01',
    })
    expect(peakOfHistoryEvent(dataset.records, '2017', 'nino12')).toMatchObject({
      value: 1.7,
      month: '2017-03',
    })
  })

  it('exposes the three historical events and the data-derived current year', async () => {
    const full = await loadDataset('noaa-ersst')
    const dataset = shapeHistoricoDataset(full)

    expect(historyEventSelectorData(dataset.records)).toEqual([
      '1982-83',
      '1997-98',
      '2017',
      CURRENT_EVENT_ID,
    ])
    expect(dataset.records.length).toBeLessThan(full.records.length)
    expect(
      dataset.records.every((record) => record.event || record.start.startsWith('2026-')),
    ).toBe(true)
  })

  it('keeps a missing month as a gap instead of shifting later values', async () => {
    const dataset = await loadDataset('noaa-ersst')
    const records = dataset.records.filter((record) => record.start !== '1982-08')
    const aligned = alignHistoryEvent(records, '1982-83', 'nino34')

    expect(aligned[1]).toEqual({ offset: 2, month: '1982-08', value: null })
    expect(aligned[2]).toEqual({ offset: 3, month: '1982-09', value: 1.45 })
  })

  it('aligns and computes official ONI separately from the monthly ERSST series', async () => {
    const full = await loadDataset('noaa-cpc-oni')
    const dataset = shapeHistoricoOniDataset(full)

    expect(alignHistoryOniEvent(dataset.records, '1982-83')[0]).toEqual({
      offset: 1,
      month: '1982-07',
      value: 0.78,
    })
    expect(peakOfHistoryOniEvent(dataset.records, '1982-83')).toMatchObject({
      value: 2.14,
      month: '1983-01',
    })
    expect(dataset.records.length).toBeLessThan(full.records.length)
  })
})
