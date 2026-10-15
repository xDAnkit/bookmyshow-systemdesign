export interface Show {
  id: string;
  cinemaId: string;
  movieTitle: string;
  language: string;
  format: string;
  startsAt: string; // ISO 8601 with offset
  price: number;
}

export interface ShowsByCinemaParams {
  cinemaId: string;
}
