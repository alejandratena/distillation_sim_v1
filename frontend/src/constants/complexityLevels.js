const complexityLevels = {
  foundational: {
    label: 'Foundational',
    score: 30,
    assumptions: [
      'Steady-state operation assumed',
      'Ideal vapor-liquid equilibrium (Raoult\'s Law)',
      'No heat losses to surroundings',
      'Constant molar overflow (CMO) assumed',
      'Binary system only (Water / Ethanol)',
      'No pressure drop across column',
      'Feed assumed to be a saturated liquid',
    ],
  },

  intermediate: {
    label: 'Intermediate',
    score: 55,
    assumptions: [],
  },

  advancedAcademic: {
    label: 'Advanced Academic',
    score: 72,
    assumptions: [],
  },

  preIndustry: {
    label: 'Pre-Industry',
    score: 88,
    assumptions: [],
  },

  industry: {
    label: 'Industry',
    score: 97,
    assumptions: [],
  },
}

export default complexityLevels