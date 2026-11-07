import { signToken } from './internal/token.js';

export function issueSession(userId) {
    return signToken({ sub: userId });
}
