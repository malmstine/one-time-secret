from server.utils import Secret


def test_base_usage_with_password():
    password = "wrong_password"
    secret_text = "red panda attacks"
    s = Secret(password=password)
    cipher_text, tag = s.encrypt(secret_text)
    assert cipher_text, cipher_text
    assert tag, tag

    decrypted = s.decrypt(cipher_text, tag)
    assert decrypted == secret_text


def test_base_usage_without_password():
    secret_text = "red panda attacks"
    s = Secret()
    cipher_text, tag = s.encrypt(secret_text)
    assert cipher_text, cipher_text
    assert tag, tag

    decrypted = s.decrypt(cipher_text, tag)
    assert decrypted == secret_text

    s = Secret()
    decrypted = s.decrypt(cipher_text, tag)
    assert decrypted == secret_text


def test_base_usage_with_wrong_user_password():
    password = "wrong_password"
    secret_text = "red panda attacks"
    wrong_password = "another_password"
    s = Secret(password=password)
    cipher_text, tag = s.encrypt(secret_text)
    assert cipher_text, cipher_text
    assert tag, tag

    s = Secret(password=wrong_password)
    decrypted = s.decrypt(cipher_text, tag, raise_exception=False)
    assert decrypted is None, decrypted


def test_base_usage_with_wrong_password():
    secret_text = "red panda attacks"
    wrong_password = "another_password"
    s = Secret()
    cipher_text, tag = s.encrypt(secret_text)
    assert cipher_text, cipher_text
    assert tag, tag

    s = Secret(password=wrong_password)
    decrypted = s.decrypt(cipher_text, tag, raise_exception=False)
    assert decrypted is None, decrypted
