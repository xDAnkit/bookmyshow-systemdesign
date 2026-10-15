export interface Cinema {
  id: string;
  cityId: string;
  name: string;
  address: string;
}

export interface CinemasByCityParams {
  cityId: string;
}
