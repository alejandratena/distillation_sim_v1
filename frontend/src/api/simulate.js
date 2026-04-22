import { apiPost } from './client'

export async function runDistillationSimulation(inputs) {
  return apiPost('/simulate/distillation', {
    feed_stream: {
      temperature: Number(inputs.feedTemperature),
      pressure: Number(inputs.feedPressure),
      mass_flow: Number(inputs.feedMassFlow),
      composition: {
        Water: Number(inputs.waterFraction),
        Ethanol: Number(inputs.ethanolFraction),
      },
    },
    distillate_split: {
      Water: Number(inputs.waterToDistillate),
      Ethanol: Number(inputs.ethanolToDistillate),
    },
    bottoms_split: {
      Water: 1 - Number(inputs.waterToDistillate),
      Ethanol: 1 - Number(inputs.ethanolToDistillate),
    },
    distillate_temperature: Number(inputs.distillateTemperature),
    bottoms_temperature: Number(inputs.bottomsTemperature),
    pressure: Number(inputs.columnPressure),
  })
}