import FeedTankNode from './FeedTankNode'
import DistillationColumnNode from './DistillationColumnNode'
import CondenserNode from './CondenserNode'
import ReboilerNode from './ReboilerNode'
import HeatExchangerNode from './HeatExchangerNode'

const nodeTypes = {
  feedTank: FeedTankNode,
  distillationColumn: DistillationColumnNode,
  condenser: CondenserNode,
  reboiler: ReboilerNode,
  heatExchanger: HeatExchangerNode,
}

export default nodeTypes