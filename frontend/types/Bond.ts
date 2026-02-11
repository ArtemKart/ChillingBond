export interface BondHolderResponse {
    id: string;
    quantity: number;
    purchase_date: string; // ISO date string
    last_update: string | null; // ISO datetime string
    bond_id: string;
    series: string;
    nominal_value: number;
    maturity_period: number;
    initial_interest_rate: number;
    first_interest_period: number;
    reference_rate_margin: number;
}
