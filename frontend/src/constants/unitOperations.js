import { Cylinder, Columns2, Thermometer, Flame, ArrowLeftRight } from 'lucide-react'

const unitOperations = [
  {
    id: 'feedTank',
    label: 'Feed Tank',
    icon: Cylinder,
    nodeType: 'feedTank',
  },
  {
    id: 'distillationColumn',
    label: 'Distillation Column',
    icon: Columns2,
    nodeType: 'distillationColumn',
  },
  {
    id: 'condenser',
    label: 'Condenser',
    icon: Thermometer,
    nodeType: 'condenser',
  },
  {
    id: 'reboiler',
    label: 'Reboiler',
    icon: Flame,
    nodeType: 'reboiler',
  },
  {
    id: 'heatExchanger',
    label: 'Heat Exchanger',
    icon: ArrowLeftRight,
    nodeType: 'heatExchanger',
  },
]

export default unitOperations