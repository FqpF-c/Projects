import random
def generate_private_key(p):
 return random.randint(2, p - 2)
def compute_public_key(base, private_key, prime):
 return pow(base, private_key, prime)
def compute_shared_secret(public_key, private_key, prime):
 return pow(public_key, private_key, prime)
def diffie_hellman_key_exchange():
 p = 23 
 g = 5 
 alice_private = generate_private_key(p)
 alice_public = compute_public_key(g, alice_private, p)
 bob_private = generate_private_key(p)
 bob_public = compute_public_key(g, bob_private, p)
 alice_shared_secret = compute_shared_secret(bob_public, alice_private, p)
 bob_shared_secret = compute_shared_secret(alice_public, bob_private, p)
 assert alice_shared_secret == bob_shared_secret, "Key exchange failed!"
 print("Alice's Private Key:", alice_private)
 print("Alice's Public Key:", alice_public)
 print("Bob's Private Key:", bob_private)
 print("Bob's Public Key:", bob_public)
 print("Shared Secret Key:", alice_shared_secret)


diffie_hellman_key_exchange()