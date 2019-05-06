function run () {
    LANG=en_US.UTF-8 ./$@
    RETURN=$?
    return $RETURN
}
