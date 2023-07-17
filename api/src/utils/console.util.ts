import readline from 'readline';

/**
 * Promisifies the `rl.question` method of the `readline.Interface` to allow using it with async/await syntax.
 *
 * @description This function wraps the asynchronous `rl.question` method in a Promise and returns a Promise
 * that resolves to the user's input (answer) once they provide it. It allows you to use `await` with `rl.question`
 * in an async function, making it more convenient to handle user input in a synchronous manner.
 *
 * @param {readline.Interface} rl - The `readline.Interface` object to use for user input.
 * @param {string} prompt - The prompt to display to the user before waiting for input.
 * @returns {Promise<string>} A Promise that resolves to the user's input (answer) provided via `rl.question`.
 *
 * @example
 * // Example usage:
 * async function getUserInput() {
 *   const rl = readline.createInterface({
 *     input: process.stdin,
 *     output: process.stdout
 *   });
 *
 *   try {
 *     const answer = await promisifiedQuestion(rl, 'Enter your name: ');
 *     console.log(`Hello, ${answer}!`);
 *   } catch (error) {
 *     console.error('Error occurred while getting user input:', error);
 *   } finally {
 *     rl.close();
 *   }
 * }
 *
 * getUserInput();
 */
function promisifiedQuestion(
  rl: readline.Interface,
  prompt: string
): Promise<string> {
  return new Promise(resolve => {
    rl.question(prompt, answer => {
      resolve(answer);
    });
  });
}

/**
 * Asynchronously reads a line from the user input (stdin) with the provided prompt.
 *
 * @description This function uses the Node.js `readline` module to asynchronously read a line from the user's input (stdin).
 * It displays the specified `prompt` to the user before waiting for their input. The function returns a Promise that resolves
 * to the user's input (answer) once they provide it. It closes the readline interface automatically after reading the input.
 *
 * @param {string} prompt - The prompt to display to the user before waiting for input.
 * @returns {Promise<string>} A Promise that resolves to the user's input (answer) provided via stdin.
 *
 * @example
 * // Example usage:
 * async function getUserInput() {
 *   try {
 *     const answer = await asyncReadLine('Enter your name: ');
 *     console.log(`Hello, ${answer}!`);
 *   } catch (error) {
 *     console.error('Error occurred while getting user input:', error);
 *   }
 * }
 *
 * getUserInput();
 */
export async function asyncReadLine(prompt: string): Promise<string> {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  try {
    return await promisifiedQuestion(rl, prompt);
  } finally {
    rl.close();
  }
}
