import notify2

if __name__ == "__main__":
    notify2.init("Tarun APpp")
    n = notify2.Notification(summary="Hi Tarun, This is new quotes for you",
                             message="The most difficult thing is the decision to act, the rest is merely tenacity.")
    n.show()
