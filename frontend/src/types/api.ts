/* Types mirroring backend/schemas.py */

export interface RoofDTO {
  width_m: number;
  length_m: number;
  monthly_consumption_kwh: number;
  city: string;
  roof_type: string;
  max_budget_brl: number | null;
}

export interface GAConfigDTO {
  population_size: number;
  generations: number;
  crossover_rate: number;
  mutation_rate: number;
  elitism_count: number;
  random_seed: number;
  cost_weight_alpha: number;
  waste_penalty_weight: number;
  deficit_penalty_weight: number;
  budget_penalty_weight: number;
}

export interface GenerationStatsDTO {
  generation: number;
  best_fitness: number;
  avg_fitness: number;
  best_panels: number;
}

export interface ScenarioRunResultDTO {
  execution_label: string;
  city: string;
  best_num_panels: number;
  best_fitness: number;
  best_energy_kwh_month: number;
  best_cost_brl: number;
  monthly_consumption_kwh: number;
  roof_area_m2: number;
  roof_usable_area_m2: number;
  roof_occupancy_ratio: number;
  panel_area_m2: number;
  energy_surplus_kwh: number;
  energy_deficit_kwh: number;
  benchmark_panels: number;
  benchmark_fitness: number;
  benchmark_energy_kwh_month: number;
  benchmark_cost_brl: number;
  budget_limit_brl: number | null;
  under_budget: boolean;
  execution_time_s: number;
  generations: number;
  run_seed: number;
}

export interface FitnessBreakdownDTO {
  energy_term: number;
  cost_penalty: number;
  waste_penalty: number;
  deficit_penalty: number;
  area_penalty: number;
  budget_penalty: number;
  fitness_total: number;
  energy_kwh: number;
  cost_brl: number;
}

export interface OptimizationOutcomeDTO {
  result: ScenarioRunResultDTO;
  history: GenerationStatsDTO[];
  summary: Record<string, unknown>;
  final_population: { num_panels: number; fitness: number; id: string }[];
  fitness_breakdown: FitnessBreakdownDTO | null;
}

export interface BaselineResponse {
  panels: number;
  fitness: number;
  energy_kwh_month: number;
  cost_brl: number;
}

export interface SensitivityPointDTO {
  consumption_kwh: number;
  best_panels: number;
  best_fitness: number;
  execution_time_s: number;
}

export interface TimingPointDTO {
  label: string;
  parameter_value: number;
  execution_time_s: number;
  best_panels: number;
}