export function signToken(claims) {
    return Buffer.from(JSON.stringify(claims)).toString('base64url');
}
