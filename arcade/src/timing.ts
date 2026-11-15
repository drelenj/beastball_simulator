import { DT } from './engine';

/** Rendering contributes time, never randomness or a variable physics step. */
export class FixedStepper {
  accumulator = 0;
  advance(seconds: number, speed: number, step: () => void, limit = 120) {
    this.accumulator += Math.max(0, seconds) * speed;
    let count = 0;
    while (this.accumulator + 1e-10 >= DT && count < limit) {
      step(); this.accumulator -= DT; count++;
    }
    return count;
  }
  reset() { this.accumulator = 0; }
}
