export class AppError extends Error {
  readonly statusCode: number;
  readonly code: string;

  constructor(statusCode: number, code: string, message: string) {
    super(message);
    this.statusCode = statusCode;
    this.code = code;
  }
}

export const notFound = (message: string): AppError => new AppError(404, "NOT_FOUND", message);

export const serviceUnavailable = (message: string): AppError =>
  new AppError(503, "SERVICE_UNAVAILABLE", message);
